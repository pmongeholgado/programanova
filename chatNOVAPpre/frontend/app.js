const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("inputMessage");
const sendBtn = document.getElementById("sendBtn");
const speakBtn = document.getElementById("speakBtn");
const readLastBtn = document.getElementById("readLastBtn");
const newChatBtn = document.getElementById("newChatBtn");
const chatListEl = document.getElementById("chatList");

/* ---------- API LOCAL / RED DEFINITIVA ---------- */

function getApiBaseUrl() {
  const host = location.hostname;

  const isLocal =
    host === "127.0.0.1" ||
    host === "localhost" ||
    host.endsWith(".local");

  if (isLocal) {
    return "http://127.0.0.1:8000/stream";
  }

  return "https://programanova-production.up.railway.app/stream";
}

const API_BASE_URL = getApiBaseUrl();

/* ---------- ESTADO ---------- */

let chats = [];
let activeChatId = null;
let isSending = false;

/* ---------- PERSISTENCIA ---------- */

function saveState() {
  localStorage.setItem("novap_chats", JSON.stringify(chats));
  localStorage.setItem("novap_active", activeChatId || "");
}

function loadState() {
  try {
    const saved = localStorage.getItem("novap_chats");
    const savedActive = localStorage.getItem("novap_active");

    chats = saved ? JSON.parse(saved) : [];
    activeChatId = savedActive || null;
  } catch {
    chats = [];
    activeChatId = null;
  }
}

/* ---------- MARKDOWN / FORMATEO REAL ---------- */

if (window.marked && typeof window.marked.setOptions === "function") {
  window.marked.setOptions({
    gfm: true,
    breaks: true,
    highlight: function (code, lang) {
      if (window.hljs) {
        const language = window.hljs.getLanguage(lang) ? lang : "plaintext";
        return window.hljs.highlight(code, { language }).value;
      }
      return code;
    }
  });
}

function formatText(text) {
  if (!text) return "";

  if (!window.marked || typeof window.marked.parse !== "function") {
    return text
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\n/g, "<br>");
  }

  let html = window.marked.parse(text);

  if (window.DOMPurify && typeof window.DOMPurify.sanitize === "function") {
    html = window.DOMPurify.sanitize(html);
  }

  return html;
}

/* ---------- RENDER RICO DE BOT ---------- */

function buildBotContentHtml(text, imageUrl = null, audioUrl = null) {
  let html = formatText(text || "");

  if (imageUrl) {
    html += `
      <div style="margin-top:12px;">
        <img
          src="${imageUrl}"
          alt="Imagen generada por chatNOVAP"
          style="max-width:100%; border-radius:12px; display:block;"
        >
      </div>
    `;
  }

  if (audioUrl) {
    html += `
      <div style="margin-top:12px;">
        <audio controls src="${audioUrl}" style="width:100%;"></audio>
      </div>
    `;
  }

  return html;
}


function escapePremiumHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function absolutePremiumUrl(url) {
  if (!url || typeof url !== "string") return null;
  let clean = url.trim();
  if (!clean) return null;

  if (clean.startsWith("http://") || clean.startsWith("https://")) {
    return clean;
  }

  if (clean.startsWith("/static/") || clean.startsWith("/video-status/")) {
    return "https://genesios.online" + clean;
  }

  return clean;
}

function premiumResourceLabel(url) {
  const lower = String(url || "").toLowerCase();

  if (lower.includes("video-status")) return "Estado del vídeo";
  if (lower.includes(".mp4")) return "Ver / descargar MP4";
  if (lower.includes(".zip")) return "Descargar ZIP completo";
  if (lower.includes("index.html") || lower.includes(".html")) return "Abrir página HTML";
  if (lower.includes(".md")) return "Guion Markdown";
  if (lower.includes(".txt")) return "Guion TXT";
  if (lower.includes(".json")) return "JSON de escenas";
  if (lower.includes(".mp3") || lower.includes(".wav")) return "Audio";
  if (lower.match(/\.(png|jpg|jpeg|webp|gif)(\?|$)/)) return "Imagen";
  return "Recurso premium";
}

function collectPremiumUrlsFromAny(value, set) {
  if (value == null) return;

  if (typeof value === "string") {
    const direct = absolutePremiumUrl(value);
    if (
      direct &&
      (
        direct.startsWith("http") ||
        direct.startsWith("/static/") ||
        direct.startsWith("/video-status/") ||
        direct.includes(".mp4") ||
        direct.includes(".zip") ||
        direct.includes(".html") ||
        direct.includes(".md") ||
        direct.includes(".txt") ||
        direct.includes(".json") ||
        direct.includes(".mp3") ||
        direct.includes(".png") ||
        direct.includes(".jpg") ||
        direct.includes(".jpeg") ||
        direct.includes(".webp")
      )
    ) {
      set.add(direct);
    }

    const markdownLinks = value.matchAll(/\[[^\]]+\]\(([^)]+)\)/g);
    for (const match of markdownLinks) {
      const u = absolutePremiumUrl(match[1]);
      if (u) set.add(u);
    }

    const rawUrls = value.matchAll(/https?:\/\/[^\s)"']+/g);
    for (const match of rawUrls) {
      const u = absolutePremiumUrl(match[0]);
      if (u) set.add(u);
    }

    return;
  }

  if (Array.isArray(value)) {
    value.forEach(v => collectPremiumUrlsFromAny(v, set));
    return;
  }

  if (typeof value === "object") {
    Object.values(value).forEach(v => collectPremiumUrlsFromAny(v, set));
  }
}

function buildPremiumExtrasHtml(data) {
  const urls = new Set();

  collectPremiumUrlsFromAny(data.resource_urls, urls);
  collectPremiumUrlsFromAny(data.resourceUrls, urls);
  collectPremiumUrlsFromAny(data.video_status_url, urls);
  collectPremiumUrlsFromAny(data.videoStatusUrl, urls);
  collectPremiumUrlsFromAny(data.image_url, urls);
  collectPremiumUrlsFromAny(data.audio_url, urls);
  collectPremiumUrlsFromAny(data.chart_url, urls);
  collectPremiumUrlsFromAny(data.visual, urls);
  collectPremiumUrlsFromAny(data.reply, urls);
  collectPremiumUrlsFromAny(data.raw, urls);

  const list = Array.from(urls).filter(Boolean);

  if (!list.length) return "";

  const mp4 = list.find(u => String(u).toLowerCase().includes(".mp4"));

  let html = "";

  if (mp4) {
    html += `
      <div class="premium-video" style="margin-top:14px;">
        <video controls src="${escapePremiumHtml(mp4)}" style="width:100%;max-height:420px;border-radius:14px;"></video>
      </div>
    `;
  }

  html += `
    <div class="premium-resources" style="margin-top:16px;">
      <strong>Recursos premium disponibles:</strong>
      <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;">
  `;

  list.forEach((url) => {
    html += `
      <a href="${escapePremiumHtml(url)}"
         target="_blank"
         rel="noopener noreferrer"
         style="display:inline-block;padding:8px 10px;border-radius:10px;background:#2f66ff;color:white;text-decoration:none;font-weight:600;">
        ${escapePremiumHtml(premiumResourceLabel(url))}
      </a>
    `;
  });

  html += `
      </div>
    </div>
  `;

  if (data.video_job_id || data.videoJobId || data.video_status_url || data.videoStatusUrl) {
    html += `
      <div style="margin-top:12px;font-size:0.95em;opacity:0.9;">
        Vídeo premium detectado${data.video_job_id || data.videoJobId ? ": " + escapePremiumHtml(data.video_job_id || data.videoJobId) : ""}.
      </div>
    `;
  }

  return html;
}


/* ---------- UI ---------- */

function scrollMessagesToBottom() {
  requestAnimationFrame(() => {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  });
}


function startVoiceInput() {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    alert("Tu navegador no soporta dictado por voz.");
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.lang = "es-ES";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  if (speakBtn) {
    speakBtn.disabled = true;
    speakBtn.textContent = "🎙️ Escuchando...";
  }

  recognition.onresult = (event) => {
    const transcript = event.results?.[0]?.[0]?.transcript || "";
    const current = inputEl.value.trim();

    inputEl.value = current
      ? current + " " + transcript
      : transcript;

    inputEl.focus();
  };

  recognition.onerror = () => {
    alert("No se pudo usar el micrófono. Revisa permisos del navegador.");
  };

  recognition.onend = () => {
    if (speakBtn) {
      speakBtn.disabled = false;
      speakBtn.textContent = "🎤 Hablar";
    }
  };

  recognition.start();
}


function readLastBotMessage() {
  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  const botMessages = chat.messages.filter(
    m => m.sender === "bot" && m.text && m.text.trim()
  );
  if (!botMessages.length) return;

  const lastBotMessage = botMessages[botMessages.length - 1].text;

  if (!("speechSynthesis" in window)) {
    alert("Tu navegador no soporta lectura por voz.");
    return;
  }

  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(lastBotMessage);
  utterance.lang = "es-ES";
  utterance.rate = 1;
  utterance.pitch = 1;

  window.speechSynthesis.speak(utterance);
}


function normalizeMessage(messageOrText, sender) {
  if (typeof messageOrText === "string") {
    return {
      text: messageOrText,
      sender,
      imageUrl: null,
      audioUrl: null,
      premiumHtml: ""
    };
  }

  return {
    text: messageOrText.text || "",
    sender: messageOrText.sender || sender || "bot",
    imageUrl: messageOrText.imageUrl || null,
    audioUrl: messageOrText.audioUrl || null,
    premiumHtml: messageOrText.premiumHtml || ""
  };
}



function addMessageToDOM(messageOrText, sender) {
  const message = normalizeMessage(messageOrText, sender);

  const div = document.createElement("div");
  div.classList.add("message", message.sender);

  if (message.sender === "user") {
    div.textContent = message.text;
  } else {
    div.innerHTML = buildBotContentHtml(message.text, message.imageUrl, message.audioUrl) + (message.premiumHtml || "");
  }

  messagesEl.appendChild(div);
  scrollMessagesToBottom();

  return div;
}


function renderMessages() {
  messagesEl.innerHTML = "";

  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  chat.messages.forEach(m => addMessageToDOM(m, m.sender));
}

function renderChatList() {
  chatListEl.innerHTML = "";

  chats.forEach(chat => {
    const container = document.createElement("div");
    container.classList.add("chat-item");

    if (chat.id === activeChatId) {
      container.classList.add("active");
    }

    const title = document.createElement("div");
    title.classList.add("chat-title");
    title.textContent = chat.title;

    title.ondblclick = (e) => {
      e.stopPropagation();

      const newTitle = prompt("Nuevo nombre:", chat.title);

      if (newTitle) {
        chat.title = newTitle;
        saveState();
        renderChatList();
      }
    };

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "🗑";
    deleteBtn.type = "button";

    deleteBtn.onclick = (e) => {
      e.stopPropagation();
      deleteChat(chat.id);
    };

    container.appendChild(title);
    container.appendChild(deleteBtn);

    container.onclick = () => {
      activeChatId = chat.id;
      saveState();
      renderChatList();
      renderMessages();
    };

    chatListEl.appendChild(container);
  });
}

/* ---------- CHATS ---------- */

function createNewChat() {
  const id = Date.now().toString();

  chats.unshift({
    id,
    title: "Nueva conversación",
    messages: [
      {
        text: "Hola 👋 Bienvenido a chatNOVAP",
        sender: "bot",
        imageUrl: null,
        audioUrl: null
      }
    ]
  });

  activeChatId = id;

  saveState();
  renderChatList();
  renderMessages();
}

function deleteChat(id) {
  chats = chats.filter(c => c.id !== id);

  if (activeChatId === id) {
    activeChatId = chats.length ? chats[0].id : null;
  }

  if (!activeChatId) {
    createNewChat();
    return;
  }

  saveState();
  renderChatList();
  renderMessages();
}

/* ---------- ENVÍO RICO CON APOYO EN GENESIOS ---------- */

async function sendMessage() {
  if (isSending) return;

  const text = inputEl.value.trim();
  if (!text) return;

  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  isSending = true;

  chat.messages.push({
    text,
    sender: "user",
    imageUrl: null,
    audioUrl: null
  });

  if (chat.title === "Nueva conversación") {
    chat.title = text.substring(0, 30);
  }

  inputEl.value = "";
  inputEl.focus();

  saveState();
  renderChatList();
  renderMessages();

  const messageDiv = addMessageToDOM(
    {
      text: "NOVA está escribiendo...",
      sender: "bot",
      imageUrl: null,
      audioUrl: null
    },
    "bot"
  );
  messageDiv.style.opacity = "0.7";

  let dots = 0;
  const typingInterval = setInterval(() => {
    dots = (dots + 1) % 4;
    messageDiv.innerHTML = buildBotContentHtml(
      "NOVA está escribiendo" + ".".repeat(dots),
      null,
      null
    );
  }, 400);

  try {
    const url = `${API_BASE_URL}/rich-reply?chat_id=${encodeURIComponent(activeChatId)}&message=${encodeURIComponent(text)}`;
    const res = await fetch(url, {
      method: "POST"
    });

    if (!res.ok) {
      throw new Error("Respuesta no válida del servidor");
    }

    const data = await res.json();

    clearInterval(typingInterval);
    messageDiv.style.opacity = "1";

    const finalText = data.reply || "No se pudo obtener respuesta.";
    const imageUrl = data.image_url || null;
    const audioUrl = data.audio_url || null;
    const premiumHtml = buildPremiumExtrasHtml(data);

    messageDiv.innerHTML = buildBotContentHtml(finalText, imageUrl, audioUrl) + premiumHtml;

    chat.messages.push({
      text: finalText,
      sender: "bot",
      imageUrl,
      audioUrl,
      premiumHtml
    });

    if (audioUrl) {
      try {
        const audio = new Audio(audioUrl);
        audio.play().catch(() => {});
      } catch (_) {}
    }
  } catch (err) {
    clearInterval(typingInterval);
    messageDiv.textContent = "❌ Error conectando con NOVA";
    messageDiv.style.opacity = "1";
    console.error("chatNOVAP error:", err);
  }

  isSending = false;
  saveState();
  scrollMessagesToBottom();
}

/* ---------- EVENTOS ---------- */

sendBtn.addEventListener("click", (e) => {
  e.preventDefault();
  sendMessage();
});


if (speakBtn) {
  speakBtn.addEventListener("click", (e) => {
    e.preventDefault();
    startVoiceInput();
  });
}

readLastBtn.addEventListener("click", (e) => {
  e.preventDefault();
  readLastBotMessage();
});

inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

newChatBtn.addEventListener("click", (e) => {
  e.preventDefault();
  createNewChat();
});

/* ---------- INIT ---------- */

loadState();

if (!chats.length) {
  createNewChat();
} else {
  if (!activeChatId || !chats.find(c => c.id === activeChatId)) {
    activeChatId = chats[0].id;
  }

  saveState();
  renderChatList();
  renderMessages();
}
