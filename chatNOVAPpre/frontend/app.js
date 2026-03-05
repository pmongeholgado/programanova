const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("inputMessage");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const chatListEl = document.getElementById("chatList");

/* ---------- API LOCAL / RED (FINAL DEFINITIVO) ---------- */

function getApiUrl() {

  const host = location.hostname;

  const isLocal =
    host === "127.0.0.1" ||
    host === "localhost" ||
    host.endsWith(".local");

  /* LOCAL */
  if (isLocal) {
    return "http://127.0.0.1:8000/novap/chat";
  }

  /* RED con backend explícito */
  const base = (window.__API_BASE__ || "")
    .trim()
    .replace(/\/+$/, "");

  if (base) {
    return `${base}/novap/chat`;
  }

  /* RED con reverse proxy */
  return "/novap/chat";
}

const API_URL = getApiUrl();

console.log("chatNOVAP API:", API_URL);

/* ---------- ESTADO ---------- */

let chats = [];
let activeChatId = null;
let isSending = false;

/* ---------- PERSISTENCIA FRONT ---------- */

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

/* ---------- UI ---------- */

function addMessageToDOM(text, sender) {

  const div = document.createElement("div");

  div.classList.add("message", sender);

  div.textContent = text;

  messagesEl.appendChild(div);

  messagesEl.scrollTop = messagesEl.scrollHeight;

}

function renderMessages() {

  messagesEl.innerHTML = "";

  const chat = chats.find(c => c.id === activeChatId);

  if (!chat) return;

  chat.messages.forEach(m => addMessageToDOM(m.text, m.sender));

}

function renderChatList() {

  chatListEl.innerHTML = "";

  chats.forEach(chat => {

    const container = document.createElement("div");

    container.classList.add("chat-item");

    if (chat.id === activeChatId)
      container.classList.add("active");

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
        text: "Hola Pablo 👋 Bienvenido a chatNOVAP",
        sender: "bot"
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

  if (!activeChatId)
    createNewChat();

  saveState();

  renderChatList();

  renderMessages();

}

/* ---------- ENVÍO MENSAJE ---------- */

async function sendMessage() {

  if (isSending) return;

  const text = inputEl.value.trim();

  if (!text) return;

  const chat = chats.find(c => c.id === activeChatId);

  if (!chat) return;

  isSending = true;

  chat.messages.push({
    text,
    sender: "user"
  });

  if (chat.title === "Nueva conversación")
    chat.title = text.substring(0, 30);

  inputEl.value = "";

  saveState();

  renderChatList();

  renderMessages();

  const thinkingIndex =
    chat.messages.push({
      text: "NOVA está pensando…",
      sender: "bot"
    }) - 1;

  renderMessages();

  try {

    const controller = new AbortController();

    const timeout = setTimeout(() => controller.abort(), 30000);

    const res = await fetch(API_URL, {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        chat_id: activeChatId,
        message: text
      }),

      signal: controller.signal

    });

    clearTimeout(timeout);

    if (!res.ok) {

      const t = await res.text().catch(() => "");

      throw new Error(`Backend ${res.status}${t ? `: ${t}` : ""}`);

    }

    const data = await res.json();

    chat.messages[thinkingIndex] = {

      text: data.reply ?? "⚠️ Respuesta inesperada del servidor.",

      sender: "bot"

    };

  }

  catch (err) {

    chat.messages[thinkingIndex] = {

      text: `❌ Error conectando con NOVA: ${err.message}`,

      sender: "bot"

    };

  }

  isSending = false;

  saveState();

  renderMessages();

}

/* ---------- EVENTOS ---------- */

sendBtn.addEventListener("click", (e) => {

  e.preventDefault();

  sendMessage();

});

inputEl.addEventListener("keydown", (e) => {

  if (e.key === "Enter") {

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

}

else {

  if (!activeChatId || !chats.find(c => c.id === activeChatId))
    activeChatId = chats[0].id;

  saveState();

  renderChatList();

  renderMessages();

}
