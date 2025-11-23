// ===============================
//  FUNCIONES UI
// ===============================
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

// ===============================
//  ENVIAR MENSAJE AL BACKEND
// ===============================
async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user");
    input.value = "";

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ mensaje: text })
        });

        const data = await response.json();

        // 1️⃣ Mensaje principal IA
        addMessage(data.respuesta || "🤖 Nova no pudo generar una respuesta.", "bot");

        // 2️⃣ Panel lateral
        document.getElementById("emotion-value").innerText = data.emocion || "—";
        document.getElementById("intent-value").innerText = data.intencion || "—";

        // 3️⃣ Hora
        const ahora = new Date().toLocaleString();
        document.getElementById("time-value").innerText = ahora;

    } catch (error) {
        console.error("ERR:", error);
        addMessage("⚠️ Error conectando con el servidor.", "bot");
    }
}

// ===============================
//  EVENTOS
// ===============================
document.addEventListener("DOMContentLoaded", () => {

    // Enviar al pulsar botón
    document.getElementById("send-btn")
        .addEventListener("click", () => sendMessage());

    // Enviar al pulsar Enter
    document.getElementById("user-input")
        .addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                sendMessage();
            }
        });

    console.log("Frontend operativo 🔥");
});
