// ========== SEYYAH-AI - SCRIPT.JS ==========
// Kart / Blok görünümü + tıklanabilir örnek sorular + daktilo efekti

// ─────────────────────────────────────────
// ŞEHİR / KATEGORİ TESPİTİ
// Kullanıcının sorusunu analiz edip otomatik filtre üretir.
// Böylece API'ye sehir + sinif gönderilebilir.
// ─────────────────────────────────────────
const SEHIR_ANAHTAR = {
    elazig:   ["elazığ", "elazig", "harput"],
    istanbul: ["istanbul", "İstanbul", "boğaz", "bosphorus"],
    antalya:  ["antalya", "akdeniz", "kaleiçi"],
};

const SINIF_ANAHTAR = {
    history: ["tarih", "tarihçe", "geçmiş", "tarihi", "antik", "osmanlı", "bizans"],
    places:  ["gezilecek", "gezi", "yer", "mekan", "müze", "türist", "görülecek", "turist"],
    foods:   ["yemek", "yenir", "lezzet", "mutfak", "tarif", "yiyecek", "içecek", "kahvaltı"],
    gift:    ["hediye", "alınır", "hediyelik", "alışveriş", "souvenir", "ne alınır"],
};

function sorudenFiltre(soru) {
    const kucuk = soru.toLowerCase();

    let sehir = null;
    for (const [key, kelimeler] of Object.entries(SEHIR_ANAHTAR)) {
        if (kelimeler.some(k => kucuk.includes(k.toLowerCase()))) {
            sehir = key;
            break;
        }
    }

    let sinif = null;
    for (const [key, kelimeler] of Object.entries(SINIF_ANAHTAR)) {
        if (kelimeler.some(k => kucuk.includes(k))) {
            sinif = key;
            break;
        }
    }

    return { sehir, sinif };
}


// ─────────────────────────────────────────
// HTML ELEMANLARI
// ─────────────────────────────────────────
function getElements() {
    return {
        form:        document.getElementById("chat-form"),
        input:       document.getElementById("user-input"),
        responseArea:document.getElementById("response-area"),
        chatHistory: document.getElementById("chat-history"),
        newChatBtn:  document.getElementById("new-chat-btn"),
        config:      document.getElementById("config"),
    };
}

function getLogoUrl() {
    const config = document.getElementById("config");
    return config ? config.dataset.logoUrl : "/static/images/seyyah.png";
}


// ─────────────────────────────────────────
// DAKTİLO EFEKTİ
// ─────────────────────────────────────────
async function typeWriterEffect(element, text, speed = 18) {
    if (!element) return;
    element.innerHTML = "";
    let i = 0;
    return new Promise((resolve) => {
        function type() {
            if (i < text.length) {
                element.innerHTML = text.substring(0, i + 1);
                i++;
                setTimeout(type, speed);
            } else {
                resolve();
            }
        }
        type();
    });
}


// ─────────────────────────────────────────
// LOCALSTORAGE
// ─────────────────────────────────────────
let userChats   = {};
let activeChatId = null;
let currentUser  = "guest";

function saveToStorage() {
    localStorage.setItem("currentUser", currentUser);
    localStorage.setItem("userChats",   JSON.stringify(userChats));
}

function loadFromStorage() {
    const storedUser  = localStorage.getItem("currentUser");
    const storedChats = localStorage.getItem("userChats");
    if (storedUser && storedChats) {
        currentUser = storedUser;
        userChats   = JSON.parse(storedChats);
    } else {
        userChats[currentUser] = [];
    }
}


// ─────────────────────────────────────────
// ÖRNEK KART BAĞLAMA
// ─────────────────────────────────────────
function initExampleCards() {
    document.querySelectorAll('.example-card').forEach(card => {
        card.addEventListener('click', () => {
            const question = card.getAttribute('data-question');
            const input    = document.getElementById('user-input');
            if (input && question) {
                input.value = question;
                input.focus();
            }
        });
    });
}


// ─────────────────────────────────────────
// PLACEHOLDER (karşılama ekranı)
// ─────────────────────────────────────────
async function showPlaceholder() {
    const elements = getElements();
    if (!elements.responseArea) return;

    elements.responseArea.innerHTML = `
        <div class="placeholder-container">
            <img src="${getLogoUrl()}" alt="Seyyah-AI Logo" class="header-icon-inline-large" />
            <div class="welcome-text" id="welcome-text"></div>
            <div class="section-title" id="section-title" style="opacity:0;">📌 ÖRNEK SORULAR</div>
            <div class="example-grid" id="example-grid" style="opacity:0;">
                <div class="example-card" data-question="Elazığ'ın tarihi nedir?">
                    <span class="card-emoji">🏛️</span>
                    <span class="card-text">Elazığ'ın tarihi nedir?</span>
                </div>
                <div class="example-card" data-question="İstanbul'da ne yenir?">
                    <span class="card-emoji">🍽️</span>
                    <span class="card-text">İstanbul'da ne yenir?</span>
                </div>
                <div class="example-card" data-question="Antalya'dan ne hediye alınır?">
                    <span class="card-emoji">🎁</span>
                    <span class="card-text">Antalya'dan ne hediye alınır?</span>
                </div>
                <div class="example-card" data-question="Antalya'da gezilecek yerler nerelerdir?">
                    <span class="card-emoji">🏖️</span>
                    <span class="card-text">Antalya'da gezilecek yerler?</span>
                </div>
            </div>
        </div>
    `;

    const welcomeMessage = `🧭 Merhaba, ben Seyyah-AI.\nSeyahat asistanınız olarak size İstanbul, Elazığ ve Antalya hakkında bilgi verebilirim.\nTarihçe, gezilecek yerler, yöresel yemekler ve hatıra önerileri için bana sorabilirsiniz.`;
    const welcomeEl      = document.getElementById("welcome-text");

    if (welcomeEl) {
        welcomeEl.style.whiteSpace = "pre-line";
        await typeWriterEffect(welcomeEl, welcomeMessage, 25);
    }

    const sectionTitle = document.getElementById("section-title");
    const exampleGrid  = document.getElementById("example-grid");

    if (sectionTitle) { sectionTitle.style.transition = "opacity 0.5s ease"; sectionTitle.style.opacity = "1"; }
    if (exampleGrid)  { exampleGrid.style.transition  = "opacity 0.5s ease"; exampleGrid.style.opacity  = "1"; }

    initExampleCards();
}


// ─────────────────────────────────────────
// SOHBET YÖNETİMİ
// ─────────────────────────────────────────
function addNewChat() {
    if (!userChats[currentUser]) userChats[currentUser] = [];
    const chats = userChats[currentUser];
    const newId = chats.length ? Math.max(...chats.map(c => c.id)) + 1 : 1;
    chats.unshift({ id: newId, title: "Yeni Sohbet", messages: [], titleSet: false });
    saveToStorage();
    renderChatHistory();
    setActiveChat(newId);
    const el = getElements();
    if (el.input) { el.input.value = ""; el.input.focus(); }
}

function setActiveChat(id) {
    activeChatId = id;
    renderChatHistory();
    const chat = userChats[currentUser]?.find(c => c.id === id);
    if (chat?.messages.length) renderMessages();
    else showPlaceholder();
    const el = getElements();
    if (el.responseArea) el.responseArea.scrollTop = 0;
    if (el.input) el.input.value = "";
}

function renderChatHistory() {
    const el    = getElements();
    const chats = userChats[currentUser];
    if (!chats || !el.chatHistory) return;

    el.chatHistory.innerHTML = "";

    chats.forEach(chat => {
        const li = document.createElement("li");
        li.className = (chat.id === activeChatId) ? "active" : "";

        const titleSpan  = document.createElement("span");
        titleSpan.textContent = chat.title;

        const actionsDiv = document.createElement("div");
        actionsDiv.className = "chat-history-item-actions";

        const actionsBtn  = document.createElement("button");
        actionsBtn.className = "chat-history-item-actions-btn";
        actionsBtn.innerHTML = '<i class="fas fa-ellipsis-v"></i>';

        const actionsMenu = document.createElement("div");
        actionsMenu.className = "chat-history-item-actions-menu";

        const renameBtn = document.createElement("button");
        renameBtn.className = "rename-btn";
        renameBtn.innerHTML = '<i class="fas fa-pen"></i> Yeniden Adlandır';

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "delete-btn";
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Sil';

        actionsMenu.appendChild(renameBtn);
        actionsMenu.appendChild(deleteBtn);
        actionsDiv.appendChild(actionsBtn);
        actionsDiv.appendChild(actionsMenu);
        li.appendChild(titleSpan);
        li.appendChild(actionsDiv);

        li.addEventListener("click", (e) => {
            if (!e.target.closest('.chat-history-item-actions')) setActiveChat(chat.id);
        });

        actionsBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            actionsMenu.classList.toggle('show');
        });

        renameBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            actionsMenu.classList.remove('show');
            const newTitle = prompt("Yeni başlık:", chat.title);
            if (newTitle && newTitle !== chat.title) {
                chat.title = newTitle;
                saveToStorage();
                renderChatHistory();
            }
        });

        deleteBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            if (confirm("Bu sohbet silinsin mi?")) {
                userChats[currentUser] = chats.filter(c => c.id !== chat.id);
                if (activeChatId === chat.id) {
                    const remaining = userChats[currentUser];
                    activeChatId = remaining.length ? remaining[0].id : null;
                    if (activeChatId) setActiveChat(activeChatId);
                    else showPlaceholder();
                }
                saveToStorage();
                renderChatHistory();
            }
        });

        el.chatHistory.appendChild(li);
    });
}

function renderMessages() {
    const el   = getElements();
    const chat = userChats[currentUser]?.find(c => c.id === activeChatId);
    if (!chat?.messages.length || !el.responseArea) { showPlaceholder(); return; }

    el.responseArea.innerHTML = "";
    chat.messages.forEach(msg => {
        const div = document.createElement("div");
        div.classList.add("message", msg.sender === "user" ? "user-message" : "bot-message");
        div.style.whiteSpace = "pre-line";
        div.textContent = msg.text;
        el.responseArea.appendChild(div);
    });
    el.responseArea.scrollTop = el.responseArea.scrollHeight;
}


// ─────────────────────────────────────────
// BOT CEVABI (daktilo efektli)
// ─────────────────────────────────────────
async function sendBotResponse(text) {
    const el   = getElements();
    const chat = userChats[currentUser]?.find(c => c.id === activeChatId);
    if (!chat || !el.responseArea) return;

    const botDiv = document.createElement("div");
    botDiv.classList.add("message", "bot-message");
    botDiv.style.whiteSpace = "pre-line";
    el.responseArea.appendChild(botDiv);
    el.responseArea.scrollTop = el.responseArea.scrollHeight;

    await typeWriterEffect(botDiv, text, 18);

    chat.messages.push({ sender: "bot", text });
    saveToStorage();
    el.responseArea.scrollTop = el.responseArea.scrollHeight;
}


// ─────────────────────────────────────────
// YÜKLEME GÖSTERGESİ
// ─────────────────────────────────────────
function showTypingIndicator() {
    const el  = getElements();
    if (!el.responseArea) return null;

    const div = document.createElement("div");
    div.id    = "typing-indicator";
    div.classList.add("message", "bot-message");
    div.innerHTML = `<span class="typing-dots"><span>.</span><span>.</span><span>.</span></span>`;
    el.responseArea.appendChild(div);
    el.responseArea.scrollTop = el.responseArea.scrollHeight;
    return div;
}

function removeTypingIndicator() {
    document.getElementById("typing-indicator")?.remove();
}


// ─────────────────────────────────────────
// API ÇAĞRISI — /api/query
// ─────────────────────────────────────────
async function apiQuery(soru, sehir = null, sinif = null) {
    const response = await fetch("/api/query", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ soru, sehir, sinif }),
    });

    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error || `Sunucu hatası: ${response.status}`);
    }

    return response.json();   // { yanit, kaynaklar }
}


// ─────────────────────────────────────────
// FORM SUBMIT
// ─────────────────────────────────────────
function initFormListener() {
    const el = getElements();
    if (!el.form) { console.error("Form bulunamadı!"); return; }

    el.form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const text = el.input?.value.trim();
        if (!text) return;

        // Aktif sohbet yoksa yeni oluştur
        if (activeChatId === null) addNewChat();

        const chat = userChats[currentUser]?.find(c => c.id === activeChatId);
        if (!chat) return;

        // Kullanıcı mesajını kaydet ve göster
        chat.messages.push({ sender: "user", text });

        if (!chat.titleSet && chat.title === "Yeni Sohbet") {
            chat.title    = text.length > 30 ? text.slice(0, 30) + "..." : text;
            chat.titleSet = true;
            renderChatHistory();
        }

        renderMessages();
        if (el.input) { el.input.value = ""; el.input.focus(); }

        // Yükleme göstergesi
        const indicator = showTypingIndicator();

        try {
            // Şehir + kategori tespiti
            const { sehir, sinif } = sorudenFiltre(text);

            // RAG API çağrısı
            const sonuc = await apiQuery(text, sehir, sinif);

            removeTypingIndicator();
            await sendBotResponse(sonuc.yanit);

        } catch (err) {
            removeTypingIndicator();
            await sendBotResponse(`⚠️ Bir hata oluştu: ${err.message}`);
        }
    });
}


// ─────────────────────────────────────────
// YENİ SOHBET BUTONU
// ─────────────────────────────────────────
function initNewChatButton() {
    const el = getElements();
    if (el.newChatBtn) el.newChatBtn.addEventListener("click", addNewChat);
}


// ─────────────────────────────────────────
// SAYFA YÜKLENMESİ
// ─────────────────────────────────────────
window.addEventListener("DOMContentLoaded", async () => {
    console.log("Seyyah-AI başlatılıyor...");

    loadFromStorage();
    initFormListener();
    initNewChatButton();

    if (!userChats[currentUser] || userChats[currentUser].length === 0) {
        await showPlaceholder();
    } else {
        renderChatHistory();
        if (userChats[currentUser].length > 0) setActiveChat(userChats[currentUser][0].id);
        else await showPlaceholder();
    }

    const el = getElements();
    if (el.input) el.input.focus();
});