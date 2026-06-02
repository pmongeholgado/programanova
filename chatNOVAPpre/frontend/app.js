const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("inputMessage");
const sendBtn = document.getElementById("sendBtn");
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

/* ---------- UI ---------- */

function scrollMessagesToBottom() {
  requestAnimationFrame(() => {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  });
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


function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeResourceUrl(url) {
  if (!url || typeof url !== "string") return null;
  const clean = url.trim();
  if (!clean) return null;
  return clean;
}

function getFileLabel(url) {
  const clean = String(url || "");
  const lower = clean.toLowerCase();

  if (lower.includes("video-status")) return "Estado del vídeo";
  if (lower.endsWith(".mp4") || lower.includes(".mp4")) return "Descargar / ver MP4";
  if (lower.endsWith(".zip") || lower.includes(".zip")) return "Descargar ZIP completo";
  if (lower.endsWith(".html") || lower.includes("index.html")) return "Abrir página HTML";
  if (lower.endsWith(".md") || lower.includes(".md")) return "Guion Markdown";
  if (lower.endsWith(".txt") || lower.includes(".txt")) return "Guion TXT";
  if (lower.endsWith(".json") || lower.includes(".json")) return "JSON de escenas";
  if (lower.endsWith(".mp3") || lower.includes(".mp3")) return "Audio";
  if (lower.match(/\.(png|jpg|jpeg|webp|gif)(\?|$)/)) return "Imagen";
  return "Recurso premium";
}

function collectPremiumUrls(message) {
  const urls = new Set();

  const add = (value) => {
    const clean = normalizeResourceUrl(value);
    if (clean) urls.add(clean);
  };

  add(message.imageUrl);
  add(message.audioUrl);
  add(message.chartUrl);
  add(message.visual);
  add(message.videoStatusUrl);

  if (Array.isArray(message.resourceUrls)) {
    message.resourceUrls.forEach(add);
  }

  if (message.raw && typeof message.raw === "object") {
    [
      "image_url", "audio_url", "chart_url", "visual",
      "video_status_url", "videoStatusUrl",
      "download_url", "zip_url", "html_url",
      "video_url", "mp4_url"
    ].forEach(k => add(message.raw[k]));
  }

  return Array.from(urls);
}

function markdownLinksToHtml(text) {
  let safe = escapeHtml(text || "");

  safe = safe.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    function(_, label, url) {
      const cleanUrl = escapeHtml(url);
      const cleanLabel = escapeHtml(label);
      return `<a class="premium-link" href="${cleanUrl}" target="_blank" rel="noopener noreferrer">${cleanLabel}</a>`;
    }
  );

  safe = safe.replace(/\n/g, "<br>");
  return safe;
}

function buildPremiumBotContentHtml(message) {
  const textHtml = markdownLinksToHtml(message.text || "");
  const urls = collectPremiumUrls(message);

  let html = `<div class="premium-text">${textHtml}</div>`;

  const mainImage = message.imageUrl || message.visual;
  if (mainImage) {
    html += `
      <div class="premium-media">
        <img src="${escapeHtml(mainImage)}" alt="Recurso visual premium" style="max-width:100%;border-radius:14px;margin-top:14px;" />
      </div>
    `;
  }

  if (message.audioUrl) {
    html += `
      <div class="premium-audio" style="margin-top:14px;">
        <audio controls src="${escapeHtml(message.audioUrl)}" style="width:100%;"></audio>
      </div>
    `;
  }

  const mp4 = urls.find(u => String(u).toLowerCase().includes(".mp4"));
  if (mp4) {
    html += `
      <div class="premium-video" style="margin-top:14px;">
        <video controls src="${escapeHtml(mp4)}" style="width:100%;max-height:420px;border-radius:14px;"></video>
      </div>
    `;
  }

  if (urls.length) {
    html += `<div class="premium-resources" style="margin-top:16px;">`;
    html += `<strong>Recursos premium disponibles:</strong>`;
    html += `<div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:10px;">`;

    urls.forEach((url) => {
      html += `
        <a href="${escapeHtml(url)}"
           target="_blank"
           rel="noopener noreferrer"
           style="display:inline-block;padding:8px 10px;border-radius:10px;background:#2f66ff;color:white;text-decoration:none;font-weight:600;">
          ${escapeHtml(getFileLabel(url))}
        </a>
      `;
    });

    html += `</div></div>`;
  }

  if (message.videoJobId || message.videoStatusUrl) {
    html += `
      <div class="premium-status" style="margin-top:14px;font-size:0.95em;opacity:0.9;">
        Vídeo premium detectado.
        ${message.videoJobId ? "ID: " + escapeHtml(message.videoJobId) : ""}
      </div>
    `;
  }

  return html;
}



function normalizeMessage(messageOrText, sender) {
  if (typeof messageOrText === "string") {
    return {
      text: messageOrText,
      sender,
      imageUrl: null,
      audioUrl: null,
      chartUrl: null,
      visual: null,
      videoJobId: null,
      videoStatusUrl: null,
      resourceUrls: [],
      raw: null
    };
  }

  return {
    text: messageOrText.text || "",
    sender: messageOrText.sender || sender || "bot",
    imageUrl: messageOrText.imageUrl || messageOrText.image_url || null,
    audioUrl: messageOrText.audioUrl || messageOrText.audio_url || null,
    chartUrl: messageOrText.chartUrl || messageOrText.chart_url || null,
    visual: messageOrText.visual || null,
    videoJobId: messageOrText.videoJobId || messageOrText.video_job_id || null,
    videoStatusUrl: messageOrText.videoStatusUrl || messageOrText.video_status_url || null,
    resourceUrls: messageOrText.resourceUrls || messageOrText.resource_urls || [],
    raw: messageOrText.raw || null
  };
}



function addMessageToDOM(messageOrText, sender) {
  const message = normalizeMessage(messageOrText, sender);

  const div = document.createElement("div");
  div.classList.add("message", message.sender);

  if (message.sender === "user") {
    div.textContent = message.text;
  } else {
    div.innerHTML = buildPremiumBotContentHtml(message);
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

async 
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
    audioUrl: null,
    chartUrl: null,
    visual: null,
    videoJobId: null,
    videoStatusUrl: null,
    resourceUrls: [],
    raw: null
  });

  if (chat.title === "Nueva conversación") {
    chat.title = text.substring(0, 30);
  }

  inputEl.value = "";

  saveState();
  renderChatList();
  renderMessages();

  const messageDiv = addMessageToDOM(
    {
      text: "NOVA está escribiendo...",
      sender: "bot",
      imageUrl: null,
      audioUrl: null,
      chartUrl: null,
      visual: null,
      videoJobId: null,
      videoStatusUrl: null,
      resourceUrls: [],
      raw: null
    },
    "bot"
  );
  messageDiv.style.opacity = "0.7";

  let dots = 0;
  const typingInterval = setInterval(() => {
    dots = (dots + 1) % 4;
    messageDiv.innerHTML = buildPremiumBotContentHtml({
      text: "NOVA está escribiendo" + ".".repeat(dots),
      sender: "bot",
      imageUrl: null,
      audioUrl: null,
      chartUrl: null,
      visual: null,
      videoJobId: null,
      videoStatusUrl: null,
      resourceUrls: [],
      raw: null
    });
  }, 500);

  try {
    const url =
      `${API_BASE_URL}/rich-reply?chat_id=${encodeURIComponent(activeChatId)}&message=${encodeURIComponent(text)}`;

    const res = await fetch(url, {
      method: "POST"
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${errText}`);
    }

    const data = await res.json();

    clearInterval(typingInterval);
    messageDiv.style.opacity = "1";

    const finalMessage = {
      text: data.reply || "No se pudo obtener respuesta.",
      sender: "bot",
      imageUrl: data.image_url || null,
      audioUrl: data.audio_url || null,
      chartUrl: data.chart_url || null,
      visual: data.visual || null,
      videoJobId: data.video_job_id || data.videoJobId || null,
      videoStatusUrl: data.video_status_url || data.videoStatusUrl || null,
      resourceUrls: data.resource_urls || data.resourceUrls || [],
      raw: data.raw || null
    };

    messageDiv.innerHTML = buildPremiumBotContentHtml(finalMessage);

    chat.messages.push(finalMessage);
  } catch (err) {
    clearInterval(typingInterval);
    messageDiv.style.opacity = "1";
    messageDiv.textContent = "❌ Error conectando con NOVA: " + err.message;
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
