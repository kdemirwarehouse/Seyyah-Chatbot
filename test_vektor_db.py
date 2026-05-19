# ============================================
# SEYYAH-AI - VEKTÖR VERİTABANI TEST DOSYASI
# ============================================

import chromadb
from chromadb.utils import embedding_functions

# ============================================
# 1. BAĞLANTI — rag_engine.py ile AYNI model ve path
# ============================================

MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"
DB_PATH    = "vector_db/chroma_db"
COLL_NAME  = "seyyah-ai"

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)

client = chromadb.PersistentClient(path=DB_PATH)

print("✅ Vektör veritabanına bağlanıldı!")
print("📁 DB Path:", DB_PATH)

print("\n📦 Collections:", client.list_collections())

try:
    collection = client.get_collection(name=COLL_NAME, embedding_function=embedding_fn)
except Exception as e:
    print("\n❌ COLLECTION BULUNAMADI!")
    print("👉 Önce src/rag_engine.py çalıştırın.")
    print("Hata:", e)
    exit()

print(f"\n📊 Toplam vektör sayısı: {collection.count()}")
print("=" * 60)


# ============================================
# 2. SEMANTİK PREFIX — rag_engine.py ile simetrik
#    Sorgulara aynı prefix formatı eklenir:
#    "[İstanbul gezilecek yer] Sultan Ahmet Camii..."
#    Bu olmadan model query ile chunk'ı eşleştiremez.
# ============================================

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


def _build_query(sorgu: str, sehir: str = None, sinif: str = None) -> str:
    """Sorguya ingest ile aynı prefix formatını ekle."""
    parts = []
    if sehir:
        parts.append(SEHIR_LABEL.get(sehir, sehir.capitalize()))
    if sinif:
        parts.append(KATEGORI_LABEL.get(sinif, sinif))
    prefix = f"[{' '.join(parts)}] " if parts else ""
    return prefix + sorgu


# ============================================
# 3. NORMALİZASYON
# ============================================

def _normalize(text: str) -> str:
    """Türkçe karakterleri ASCII'ye çevir, küçük harf yap."""
    return (
        text.lower()
            .replace("ç", "c")
            .replace("ğ", "g")
            .replace("ı", "i")
            .replace("ş", "s")
            .replace("ö", "o")
            .replace("ü", "u")
    )


# ============================================
# 4. SORGULAMA FONKSİYONU
# ============================================

def sorgula(soru: str, sehir: str = None, sinif: str = None, sonuc_sayisi: int = 3):

    # Normalizasyon
    if sehir:
        sehir = _normalize(sehir)
    if sinif:
        sinif = sinif.lower()

    # Filtre oluştur
    filtre = None
    if sehir and sinif:
        filtre = {"$and": [{"sehir": sehir}, {"sinif": sinif}]}
        print(f"🔍 Filtre: sehir='{sehir}' + sinif='{sinif}'")
    elif sehir:
        filtre = {"sehir": sehir}
        print(f"🔍 Filtre: sehir='{sehir}'")
    elif sinif:
        filtre = {"sinif": sinif}
        print(f"🔍 Filtre: sinif='{sinif}'")
    else:
        print("🔍 Filtre: yok")

    # Semantik prefix eklenmiş sorgu
    sorgu_embed = _build_query(soru, sehir, sinif)

    print(f"\n📝 Ham sorgu      : {soru}")
    print(f"🤖 Embed sorgusu  : {sorgu_embed}")
    print("-" * 40)

    # Query
    kwargs = dict(
        query_texts=[sorgu_embed],
        n_results=sonuc_sayisi,
        include=["documents", "metadatas", "distances"],
    )
    if filtre:
        kwargs["where"] = filtre

    results = collection.query(**kwargs)

    if not results.get("documents") or not results["documents"][0]:
        print("❌ Sonuç bulunamadı!")
        return []

    output = []
    for i, doc in enumerate(results["documents"][0]):
        distance = results["distances"][0][i]
        score = round(max(0.0, 1 - distance), 3)
        output.append({
            "text":     doc,
            "metadata": results["metadatas"][0][i],
            "score":    score,
        })

    return output


# ============================================
# 5. SONUÇ GÖSTER
# ============================================

def sonuclari_goster(sonuclar):

    if not sonuclar:
        print("❌ Sonuç yok!")
        return

    for i, s in enumerate(sonuclar):
        print(f"\n{'='*50}")
        print(f"📌 SONUÇ {i+1} | SCORE: {s['score']:.3f}")
        print(f"{'='*50}")

        meta = s["metadata"]
        print(f"🏷️  Şehir    : {meta.get('sehir', '?')}")
        print(f"📂 Kategori : {meta.get('sinif', '?')}")
        print(f"📄 Dosya    : {meta.get('dosya', '?')}")

        print("\n📝 Metin:")
        print(s["text"][:400] + "...")


# ============================================
# 6. TESTLER
# ============================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🧪 SEYYAH-AI VEKTÖR TEST BAŞLIYOR")
    print("=" * 60)

    # TEST 1 — şehir + kategori filtreli
    print("\n🧪 TEST 1")
    sonuclari_goster(sorgula(
        "Elazığ'ın tarihi nedir?",
        sehir="elazig",
        sinif="history",
        sonuc_sayisi=2,
    ))

    # TEST 2 — sadece şehir filtreli
    print("\n🧪 TEST 2")
    sonuclari_goster(sorgula(
        "İstanbul'da gezilecek yerler",
        sehir="istanbul",
        sonuc_sayisi=3,
    ))

    # TEST 3 — sadece kategori filtreli
    print("\n🧪 TEST 3")
    sonuclari_goster(sorgula(
        "Antalya'da ne yenir?",
        sinif="foods",
        sonuc_sayisi=3,
    ))

    # TEST 4 — filtresiz (zor test: "yemek" → foods gelmeli)
    print("\n🧪 TEST 4")
    sonuclari_goster(sorgula(
        "yemek",
        sonuc_sayisi=3,
    ))

    # TEST 5 — şehir + kategori filtreli
    print("\n🧪 TEST 5")
    sonuclari_goster(sorgula(
        "Sultan Ahmet Camii hakkında bilgi",
        sehir="istanbul",
        sinif="places",
        sonuc_sayisi=2,
    ))

    print("\n" + "=" * 60)
    print("🎉 TESTLER TAMAMLANDI")
    print("=" * 60)