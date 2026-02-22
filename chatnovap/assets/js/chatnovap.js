// ===============================
// CHATNOVAP - Lógica básica
// ===============================

// Elementos del DOM
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const chatMessages = document.getElementById("chat-messages");

// URL del backend (la cambiaremos si hace falta)
const API_URL = "https://api.programanovapresentaciones.com/chat"; 

// Añadir mensaje al chat
function addMessage(text, sender = "user") {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);
  messageDiv.textContent = text;
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enviar mensaje
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
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error("Error en la respuesta del servidor");
    }

    const data = await response.json();

    // Ajusta según el formato que devuelva tu backend
    const reply = data.reply || data.response || "Sin respuesta";

    addMessage(reply, "bot");

  } catch (error) {
    console.error("Error:", error);
    addMessage("⚠️ Error al conectar con el servidor", "bot");
  }
});
