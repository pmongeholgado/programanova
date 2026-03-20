const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("inputMessage");
const sendBtn = document.getElementById("sendBtn");
const newChatBtn = document.getElementById("newChatBtn");
const chatListEl = document.getElementById("chatList");

/* ---------- API LOCAL / RED DEFINITIVA ---------- */

function getApiUrl() {

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

const API_URL = getApiUrl();

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

/* ---------- FORMATEO REAL DE TEXTO ---------- */



/* ---------- UI ---------- */

function addMessageToDOM(text, sender) {

  const div = document.createElement("div");

  div.classList.add("message", sender);

  // 🔵 AQUÍ ESTÁ LA CLAVE REAL
  div.innerHTML = formatText(text);

  messagesEl.appendChild(div);

  function formatText(text) {

  let html = text;

  // Negritas
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  const lines = html.split(/\n|(?=\d+\.\s)/);

  let result = "";
  let inList = false;

  lines.forEach(line => {

    line = line.trim();
    if (!line) return;

    if (/^\d+\.\s/.test(line)) {

      if (!inList) {
        result += "<ul>";
        inList = true;
      }

      result += `<li>${line.replace(/^\d+\.\s/, "")}</li>`;

    } else {

      if (inList) {
        result += "</ul>";
        inList = false;
      }

      result += `<p>${line}</p>`;
    }

  });

  if (inList) result += "</ul>";

  return result;
}requestAnimationFrame(() => {
    messagesEl.scrollTop = messagesEl.scrollHeight;
  });

  return div;

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
        text: "Hola 👋 Bienvenido a chatNOVAP",
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

/* ---------- ENVÍO ---------- */

async function sendMessage() {

  if (isSending) return;

  const text = inputEl.value.trim();
  if (!text) return;

  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;

  isSending = true;

  chat.messages.push({ text, sender: "user" });

  if (chat.title === "Nueva conversación")
    chat.title = text.substring(0, 30);

  inputEl.value = "";
  inputEl.focus();

  saveState();
  renderChatList();
  renderMessages();

  const messageDiv = addMessageToDOM("", "bot");

  messageDiv.innerHTML = "NOVA está escribiendo...";
  messageDiv.style.opacity = "0.7";

  let dots = 0;

  const typingInterval = setInterval(() => {
    dots = (dots + 1) % 4;
    messageDiv.innerHTML = "NOVA está escribiendo" + ".".repeat(dots);
  }, 400);

  try {

    const url = `${API_URL}?chat_id=${activeChatId}&message=${encodeURIComponent(text)}`;

    const res = await fetch(url);

    const reader = res.body.getReader();
    const decoder = new TextDecoder();

    let resultText = "";

    while (true) {

      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      resultText += chunk;

      clearInterval(typingInterval);

      messageDiv.innerHTML = formatText(resultText);
      messageDiv.style.opacity = "1";

      requestAnimationFrame(() => {
        messagesEl.scrollTop = messagesEl.scrollHeight;
      });

    }

    chat.messages.push({
      text: resultText,
      sender: "bot"
    });

  } catch {
    messageDiv.textContent = "❌ Error conectando con NOVA";
  }

  isSending = false;
  saveState();

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
} else {
  if (!activeChatId || !chats.find(c => c.id === activeChatId))
    activeChatId = chats[0].id;

  saveState();
  renderChatList();
  renderMessages();
}
