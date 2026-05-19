from flask import Flask, render_template, send_from_directory, request, jsonify
import os

app = Flask(__name__)


# ─────────────────────────────────────────
# query_engine'i uygulama başlarken yükle
# (her istekte yeniden yüklememek için)
# ─────────────────────────────────────────
try:
    from src.query_engine import sorgula_ve_yanitla
    RAG_AKTIF = True
    print("✅ RAG motoru yüklendi.")
except Exception as e:
    RAG_AKTIF = False
    print(f"⚠️  RAG motoru yüklenemedi: {e}")


# ─────────────────────────────────────────
# Sayfalar
# ─────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


# ─────────────────────────────────────────
# RAG API — script.js buraya POST atar
# ─────────────────────────────────────────
@app.route('/api/query', methods=['POST'])
def api_query():
    if not RAG_AKTIF:
        return jsonify({"error": "RAG motoru aktif değil. Lütfen src/query_engine.py dosyasını kontrol edin."}), 503

    data  = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Geçersiz JSON"}), 400

    soru  = data.get("soru", "").strip()
    sehir = data.get("sehir") or None   # boş string → None
    sinif = data.get("sinif") or None

    if not soru:
        return jsonify({"error": "Soru boş olamaz"}), 400

    try:
        sonuc = sorgula_ve_yanitla(soru, sehir=sehir, sinif=sinif)
        return jsonify(sonuc)           # {"yanit": "...", "kaynaklar": [...]}
    except Exception as e:
        print(f"❌ Sorgu hatası: {e}")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)