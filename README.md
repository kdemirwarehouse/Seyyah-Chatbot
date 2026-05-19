# 🤖 Seyyah-Chatbot

Türkiye Kültür Portalı verileriyle çalışan akıllı seyahat asistanı. Flask tabanlı web arayüzü, ChromaDB vektör veritabanı ve OpenAI entegrasyonu ile İstanbul, Antalya ve Elazığ hakkında tarih, gezilecek yerler, yemek ve hediyelik önerileri sunan RAG (Retrieval-Augmented Generation) chatbot uygulamasıdır.

## ✨ Özellikler

- 🧭 **Akıllı Seyahat Rehberi:** RAG teknolojisi ile şehir bazlı sorulara bağlam odaklı cevaplar
- 🏛️ **Çok Kategorili İçerik:** Tarih, gezilecek yerler, yöresel mutfak ve hediyelik eşya
- 🌐 **Modern Web Arayüzü:** Sohbet geçmişi, örnek sorular ve daktilo efektli yanıtlar
- 🔍 **Semantik Arama:** ChromaDB ile anlamsal vektör araması
- 🇹🇷 **Türkçe Destek:** Çok dilli embedding modeli ile Türkçe sorgu anlama
- 📚 **Güvenilir Kaynak:** Yanıtlar [Türkiye Kültür Portalı](https://www.kulturportali.gov.tr/turkiye/genel) verilerine dayanır
- 💾 **Sohbet Geçmişi:** Tarayıcıda sohbetleri kaydetme ve yönetme

## 🏗️ Proje Yapısı

```
seyyah-ai/
├── app.py                      # Flask uygulaması ve API
├── requirements.txt            # Python bağımlılıkları
├── test_vektor_db.py           # Vektör DB test scripti
├── src/
│   ├── rag_engine.py           # Veri yükleme ve ChromaDB ingest
│   ├── query_engine.py         # Semantik arama ve sorgu
│   └── llm_client.py           # OpenAI entegrasyonu
├── data/
│   ├── history/                # Şehir tarihçeleri
│   ├── places/                 # Gezilecek yerler
│   ├── foods/                  # Yöresel yemekler
│   └── gift/                   # Hediyelik önerileri
├── vector_db/chroma_db/        # Vektör veritabanı
├── templates/                  # HTML şablonları
└── static/                     # CSS, JS, görseller
```

## 🚀 Kurulum

### Gereksinimler

- Python 3.10+
- OpenAI API anahtarı
- Git

### Adım 1: Projeyi Klonlayın

```bash
git clone <repository-url>
cd seyyah-ai
```

### Adım 2: Sanal Ortam Oluşturun

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

### Adım 4: Ortam Değişkenlerini Ayarlayın

Proje kök dizininde `.env` dosyası oluşturun:

```env
OPENAI_API_KEY=your_openai_api_key
```

### Adım 5: Vektör Veritabanını Oluşturun

```bash
cd src
python rag_engine.py
cd ..
```

### Adım 6: Uygulamayı Çalıştırın

```bash
python app.py
```

Uygulama **http://localhost:5000** adresinde çalışmaya başlayacaktır.

## 🔧 Kullanım

### Ana Özellikler

- **Soru Sorma:** İstanbul, Antalya veya Elazığ hakkında doğal dilde soru yazın
- **Otomatik Filtreleme:** Sistem sorudan şehir ve kategoriyi otomatik tespit eder
- **Akıllı Yanıt:** RAG sistemi kültür portalı verilerine dayalı cevap üretir
- **Sohbet Yönetimi:** Yeni sohbet oluşturma, yeniden adlandırma ve silme

### Örnek Sorular

- *Elazığ'ın tarihi nedir?*
- *İstanbul'da ne yenir?*
- *Antalya'dan ne hediye alınır?*
- *Sultan Ahmet Camii hakkında bilgi ver*

### Desteklenen Şehirler ve Kategoriler

| Şehirler | Kategoriler |
|----------|-------------|
| İstanbul | Tarih (`history`) |
| Antalya | Gezilecek yerler (`places`) |
| Elazığ | Yemek (`foods`) |
| | Hediyelik (`gift`) |

## 🛠️ Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Flask, Python |
| **AI/ML** | OpenAI GPT-4.1-mini, LangChain |
| **Vektör DB** | ChromaDB |
| **Embedding** | Sentence Transformers (`paraphrase-multilingual-mpnet-base-v2`) |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Veri** | [Türkiye Kültür Portalı](https://www.kulturportali.gov.tr/turkiye/genel) |

## 📁 Önemli Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `app.py` | Flask sunucusu ve `/api/query` endpoint'i |
| `src/rag_engine.py` | Veri chunk'lama ve vektör DB oluşturma |
| `src/query_engine.py` | Semantik arama ve skor filtreleme |
| `src/llm_client.py` | OpenAI prompt ve yanıt üretimi |
| `static/js/script.js` | Sohbet arayüzü ve API çağrıları |
| `data/` | Kültür portalından derlenen metin verileri |

## 🔒 Güvenlik

- OpenAI API anahtarı `.env` dosyasında tutulur
- `.env` dosyasını versiyon kontrolüne eklemeyin
- Üretim ortamında Flask `debug` modunu kapatın

## 📞 İletişim

Proje hakkında sorularınız için:

- **E-posta:** emingunes723@gmail.com

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!
