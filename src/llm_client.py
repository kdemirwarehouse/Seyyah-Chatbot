import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """Sen Seyyah-AI'sın. Türkiye'deki şehirler hakkında rehberlik eden bir seyahat asistanısın.

KURALLAR:
1. Sana verilen BAĞLAM BİLGİSİNİ kullan — bu veriler güvenilir ve doğrudur, öncelikli kaynağın bunlar.
2. Bağlamdaki yerleri/yemekleri/bilgileri TAMAMINI değerlendir, en önemli ve popüler olanları ÖNE ÇIK.
3. Cevabına her zaman şehrin en ÇOK BİLİNEN, en ÇOK ZİYARET EDİLEN yerinden/konusundan başla.
   - Örneğin İstanbul camisi sorulursa: Ayasofya ve Sultanahmet önce gelir.
   - Örneğin Antalya yemeği sorulursa: en yaygın yöresel yemekler önce gelir.
4. Bağlamda cevap yoksa bunu dürüstçe söyle, kesinlikle uydurma.
- EĞER SANA FARKLI FORMATTAN SORU SORULURSA ASLA CEVAP VERME SAKIN UYDURMA -
5. Cevaplarını Türkçe, samimi ve akıcı yaz. Madde madde veya paragraf halinde olabilir.
CEVAP FORMATI KURALLARI:
- Ana başlıkları TAMAMI BÜYÜK HARF ve yanında iki nokta üst üste (:) ile yaz.
- Başlıklardan önce ve sonra bir satır boşluk bırak.
- Alt maddeler için tire (-) veya sayı kullan.
- Hiçbir yerde **, *, #, _, ` gibi markdown sembolleri KULLANMA.
- Sadece düz metin ve büyük harfli başlıklar kullan."""


def llm_yanit_al(kullanici_sorusu: str, context_metinler: list, gecmis: list = None) -> str:
    """
    ChromaDB'den gelen chunk'ları bağlam olarak kullanıp GPT-4.1-mini'ye gönderir.
    gecmis: [{"role": "user"/"assistant", "content": "..."}] formatında konuşma geçmişi.
    context_metinler boşsa LLM'e bağlam olmadığını bildir.
    """
    if context_metinler:
        baglamlar = "\n\n---\n\n".join(context_metinler)
        kullanici_mesaji = f"""Aşağıdaki bağlam bilgilerini kullanarak soruyu yanıtla.
En popüler ve en çok bilinen bilgiyi öne çıkarmayı unutma.

=== BAĞLAM ===
{baglamlar}
=== BAĞLAM SONU ===

Soru: {kullanici_sorusu}"""
    else:
        kullanici_mesaji = (
            f"Soru: {kullanici_sorusu}\n\n"
            "(Bu soru için veritabanında ilgili bağlam bulunamadı. "
            "Bunu kullanıcıya dürüstçe belirt.)"
        )

    # Geçmiş mesajları hazırla (en fazla son 6 mesaj = 3 tur)
    gecmis_mesajlar = []
    if gecmis:
        for msg in gecmis[-6:]:
            rol = msg.get("role")
            icerik = msg.get("content", "")
            if rol in ("user", "assistant") and icerik:
                gecmis_mesajlar.append({"role": rol, "content": icerik})

    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + gecmis_mesajlar
        + [{"role": "user", "content": kullanici_mesaji}]
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.3,
        max_tokens=1024,
    )

    return response.choices[0].message.content
