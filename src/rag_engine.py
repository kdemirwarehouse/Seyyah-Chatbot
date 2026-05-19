# =========================
# IMPORTS
# =========================
import os
import re
import chromadb

from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions


# =========================
# 1. KATEGORİ & ŞEHİR LABEL HARİTASI
#    Chunk'lara ve sorgulara semantik prefix ekliyoruz.
#    Model "yemek" → "foods" bağlantısını çok daha iyi kurar.
# =========================
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


# =========================
# 2. TEXT CLEANING PIPELINE
# =========================
def clean_text(text: str) -> str:

    # Separator çizgileri
    text = re.sub(r"={3,}", " ", text)

    # Kaynak URL satırları
    text = re.sub(r"Kaynak\s*:\s*https?://\S+", "", text)

    # ### başlık işaretleri (metni koru, sadece işareti kaldır)
    text = re.sub(r"###\s*", "", text)

    # Çoklu whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =========================
# 3. BÖLÜM BAZLI CHUNKING
#    Önce ### başlıklarına göre mantıksal bölümlere ayır
#    (her yemek, her yer kendi bölümü olur).
#    Çok büyük bölümleri RecursiveCharacterTextSplitter ile böl.
# =========================
_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len,
)


def _split_into_sections(raw_text: str) -> list:
    """Ham metni ### başlıklarına göre bölümlere ayır."""
    parts = re.split(r"(?=###\s)", raw_text)
    return [p.strip() for p in parts if p.strip()]


def chunk_document(raw_text: str, sehir: str, kategori: str) -> list:
    """
    Metni temizle, bölümle ve her chunk'a semantik prefix ekle.

    Prefix formatı: "[İstanbul gezilecek yer ve turistik mekan]"
    Bu format ingest & query'de aynı şekilde kullanılır → simetri sağlar.
    """
    label_sehir = SEHIR_LABEL.get(sehir, sehir.capitalize())
    label_kat   = KATEGORI_LABEL.get(kategori, kategori)
    prefix      = f"[{label_sehir} {label_kat}] "

    sections    = _split_into_sections(raw_text)
    final_chunks = []

    for section in sections:
        cleaned = clean_text(section)

        if len(cleaned) < 30:          # anlamsız kısa parçaları at
            continue

        if len(cleaned) <= 800:
            final_chunks.append(prefix + cleaned)
        else:
            for sub in _splitter.split_text(cleaned):
                sub = sub.strip()
                if len(sub) >= 30:
                    final_chunks.append(prefix + sub)

    return final_chunks


# =========================
# 4. EMBEDDING MODEL
#    paraphrase-multilingual-mpnet-base-v2:
#    - distiluse'dan belirgin şekilde daha iyi Türkçe semantik anlama
#    - 50+ dil desteği, 768 boyutlu vektör
# =========================
MODEL_NAME = "paraphrase-multilingual-mpnet-base-v2"

print(f"🔄 Embedding modeli yükleniyor: {MODEL_NAME}")

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=MODEL_NAME
)

print("✅ Model hazır\n")


# =========================
# 5. CHROMA DB SETUP
#    Eski koleksiyonu sil → model değişti, eski vektörler geçersiz.
#    hnsw:space = cosine → L2'ye göre semantik arama için çok daha stabil.
# =========================
DB_PATH         = "../vector_db/chroma_db"
COLLECTION_NAME = "seyyah-ai"

client = chromadb.PersistentClient(path=DB_PATH)

# Eski koleksiyonu temizle
try:
    client.delete_collection(COLLECTION_NAME)
    print(f"🗑️  Eski '{COLLECTION_NAME}' koleksiyonu silindi.")
except Exception:
    pass

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_fn,
    metadata={"hnsw:space": "cosine"},
)

print(f"📦 Koleksiyon oluşturuldu: '{COLLECTION_NAME}'\n")


# =========================
# 6. DATA PATHS
# =========================
DATA_DIR    = "../data"
KATEGORILER = ["history", "places", "foods", "gift"]

doc_id  = 0
skipped = 0


# =========================
# 7. INGESTION PIPELINE
# =========================
for kategori in KATEGORILER:

    klasor_yolu = os.path.join(DATA_DIR, kategori)

    if not os.path.exists(klasor_yolu):
        print(f"⚠️  Klasör bulunamadı, atlanıyor: {klasor_yolu}")
        continue

    dosyalar = sorted([f for f in os.listdir(klasor_yolu) if f.endswith(".txt")])

    for dosya_adi in dosyalar:

        dosya_yolu = os.path.join(klasor_yolu, dosya_adi)
        sehir      = dosya_adi.split("_")[0]

        print(f"📄 [{kategori}] {dosya_adi}  →  şehir: {sehir}")

        with open(dosya_yolu, "r", encoding="utf-8") as f:
            raw = f.read()

        if not raw.strip():
            print("   ❌ Boş dosya, atlanıyor\n")
            skipped += 1
            continue

        # ----- chunk üret -----
        chunks = chunk_document(raw, sehir, kategori)
        print(f"   📌 {len(chunks)} chunk üretildi")

        if not chunks:
            print("   ⚠️  Hiç chunk üretilemedi, atlanıyor\n")
            skipped += 1
            continue

        # ----- toplu ekle (her dosya tek seferde) -----
        ids       = []
        documents = []
        metadatas = []

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{sehir}_{kategori}_{idx}_{doc_id}"
            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append({
                "sehir":       sehir,
                "sinif":       kategori,
                "dosya":       dosya_adi,
                "chunk_index": idx,
            })
            doc_id += 1

        collection.add(ids=ids, documents=documents, metadatas=metadatas)
        print(f"   ✅ {len(ids)} chunk eklendi\n")


# =========================
# 8. FINAL STATS
# =========================
print("=" * 50)
print("🎉 TÜM VERİLER BAŞARIYLA EKLENDİ!")
print(f"📊 Toplam chunk : {doc_id}")
print(f"⏭️  Atlanan     : {skipped} dosya")
print(f"📦 ChromaDB     : {collection.count()} kayıt")
print("=" * 50)