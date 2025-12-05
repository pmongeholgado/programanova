// ============================
// FUNCIONES UI
// ============================
function addMessage(text, sender = "bot") {
  const chatWindow = document.getElementById("chat-window");
  const msg = document.createElement("div");

  msg.classList.add("message");

  if (sender === "user") {
    msg.classList.add("user-message");
  } else {
    msg.classList.add("bot-message");
  }

  msg.innerText = text;
  chatWindow.appendChild(msg);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ============================
// ENVIAR MENSAJE AL BACKEND
// ============================
async function sendMessage() {
  const input = document.getElementById("user-input");
  const text = input.value.trim();
  if (!text) return;

  // Pintar mensaje del usuario
  addMessage(text, "user");
  input.value = "";

  try {
    const API_BASE_URL = "https://programanova.onrender.com";

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensaje: text }),
      mode: "cors",
    });

    const data = await response.json();

    // Burbuja principal IA
    addMessage(
      data.respuesta || "🤖 Nova no pudo generar una respuesta.",
      "bot"
    );

    // Pintar datos estructurados debajo
    document.getElementById("resp-respuesta").innerText =
      data.respuesta || "—";
    document.getElementById("resp-emocion").innerText =
      data.emocion || "—";
    document.getElementById("resp-intencion").innerText =
      data.intencion || "—";
    document.getElementById("resp-resultado").innerText =
      data.resultado || "—";
    document.getElementById("resp-resumen").innerText =
      data.resumen || "—";
    document.getElementById("resp-ultima").innerText =
      data.ultima_actualizacion || "—";
  } catch (error) {
    console.error("ERR /chat:", error);
    addMessage("⚠️ Error conectando con el servidor.", "bot");
  }
}

// ============================
// EVENTOS
// ============================
document.addEventListener("DOMContentLoaded", () => {
  // Conectar botón Enviar
  const sendBtn = document.getElementById("send-btn");
  if (sendBtn) {
    sendBtn.addEventListener("click", () => sendMessage());
  }

  // Conectar tecla Enter
  const userInput = document.getElementById("user-input");
  if (userInput) {
    userInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendMessage();
      }
    });
  }

  console.log("Frontend operativo 🔥");
});
