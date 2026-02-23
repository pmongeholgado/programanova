// ===============================
// CHATNOVAP - Conexión REAL backend
// ===============================

const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatMessages = document.getElementById("chat-messages");

// URL REAL de Railway
const API_URL = "https://programanovabackend-production-a426.up.railway.app/chat-open";

// Mostrar mensajes
function addMessage(text, sender = "user") {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);
  messageDiv.textContent = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const message = userInput.value.trim();
  if (!message) return;

  addMessage(message, "user");
  userInput.value = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ mensaje: message })
    });

    if (!response.ok) {
      throw new Error("Error servidor");
    }

    const data = await response.json();

    const reply = data.respuesta || "Sin respuesta";
    addMessage(reply, "bot");

  } catch (error) {
    console.error(error);
    addMessage("⚠️ Error al conectar con el servidor", "bot");
  }
});
