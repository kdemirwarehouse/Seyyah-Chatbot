import chromadb
from chromadb.utils import embedding_functions
from src.llm_client import llm_yanit_al

# ── Sabitler ──────────────────────────────────────────────
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
DB_PATH    = "vector_db/chroma_db"
COLL_NAME  = "seyyah-ai"

KATEGORI_LABEL = {
    "history": "tarih ve tarihçe",
    "places":  "gezilecek yer ve turistik mekan",
    "foods":   "yiyecek yemek tarifi mutfak lezzet",
    "gift":    "hediyelik eşya alışveriş souvenier",
}
SEHIR_LABEL = {
    "elazig":   "Elazığ",
    "istanbul": "İstanbul",
    "antalya":  "Antalya",
}

# Minimum benzerlik skoru — bunun altındaki chunk'lar bağlama eklenmez.
# Cosine similarity: 1.0 = tam eşleşme, 0.0 = alakasız
SKOR_ESIGI = 0.25

# ── ChromaDB bağlantısı ───────────────────────────────────
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection    = chroma_client.get_collection(
    name=COLL_NAME,
    embedding_function=embedding_fn
)


def _normalize(metin: str) -> str:
    return (
        metin.lower()
             .replace("ç", "c").replace("ğ", "g")
             .replace("ı", "i").replace("ş", "s")
             .replace("ö", "o").replace("ü", "u")
    )


def _build_query(sorgu: str, sehir: str = None, sinif: str = None) -> str:
    parts = []
    if sehir: parts.append(SEHIR_LABEL.get(sehir, sehir.capitalize()))
    if sinif: parts.append(KATEGORI_LABEL.get(sinif, sinif))
    prefix = f"[{' '.join(parts)}] " if parts else ""
    return prefix + sorgu


def sorgula_ve_yanitla(
    kullanici_sorusu: str,
    sehir: str = None,
    sinif: str = None,
    top_k: int = 8,          # 4→8: daha geniş havuz, LLM en iyisini seçer
) -> dict:
    """
    1) ChromaDB'de semantik arama yap (top_k=8)
    2) Skor eşiğinin altındaki chunk'ları filtrele
    3) Kalan chunk'ları skora göre sıralı olarak LLM'e ver
    4) LLM yanıtı + kaynakları döndür
    """
    if sehir: sehir = _normalize(sehir)
    if sinif: sinif = sinif.lower()

    # Filtre
    filtre = None
    if sehir and sinif:
        filtre = {"$and": [{"sehir": sehir}, {"sinif": sinif}]}
    elif sehir:
        filtre = {"sehir": sehir}
    elif sinif:
        filtre = {"sinif": sinif}

    # Semantik arama
    embed_sorgu = _build_query(kullanici_sorusu, sehir, sinif)
    kwargs = dict(
        query_texts=[embed_sorgu],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    if filtre:
        kwargs["where"] = filtre

    results   = collection.query(**kwargs)
    docs      = results["documents"][0]
    metas     = results["metadatas"][0]
    distances = results["distances"][0]

    # Skor hesapla + eşik filtresi + skora göre sırala (en yüksek önce)
    ham = []
    for doc, meta, dist in zip(docs, metas, distances):
        skor = round(max(0.0, 1 - dist), 3)
        if skor >= SKOR_ESIGI:
            ham.append({
                "metin":    doc,
                "sehir":    meta.get("sehir"),
                "kategori": meta.get("sinif"),
                "dosya":    meta.get("dosya"),
                "skor":     skor,
            })

    # Skora göre azalan sırala — en alakalı chunk bağlamın başında olur
    kaynaklar = sorted(ham, key=lambda x: x["skor"], reverse=True)

    # LLM'e gönderilecek metinler (skor sırasına göre)
    context_metinler = [k["metin"] for k in kaynaklar]

    yanit = llm_yanit_al(kullanici_sorusu, context_metinler)

    return {
        "yanit":     yanit,
        "kaynaklar": kaynaklar,
    }