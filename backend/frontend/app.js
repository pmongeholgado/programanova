// ===============================
// FUNCIONES UI
// ===============================
function addMessage(text, sender = "bot") {
    const chatWindow = document.getElementById("chat-window");
    const msg = document.createElement("div");

    msg.classList.add("message");
    msg.classList.add(sender === "user" ? "user-message" : "bot-message");

    msg.innerText = text;
    chatWindow.appendChild(msg);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ===============================
// ENVIAR MENSAJE AL BACKEND
// ===============================
async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, "user"); // Muestra mensaje del usuario
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

        // ===============================
        // RESPUESTA PRINCIPAL EN BURBUJA
        // ===============================
        addMessage(
            data.respuesta || "🤖 Nova no pudo generar respuesta.",
            "bot"
        );

        // ===============================
        // PINTAR DATOS EN PANEL INFERIOR
        // ===============================
        document.getElementById("main-answer").innerText =
            data.respuesta || "—";
        document.getElementById("emotion-value").innerText =
            data.emocion || "—";
        document.getElementById("intent-value").innerText =
            data.intencion || "—";
        document.getElementById("result-value").innerText =
            data.resultado || "—";
        document.getElementById("summary-value").innerText =
            data.resumen || "—";
        document.getElementById("time-value").innerText =
            data.ultima_actualizacion || "—";

    } catch (error) {
        console.error("ERR /chat:", error);
        addMessage("⚠️ Error conectando con el servidor.", "bot");
    }
}

// ===============================
// EVENTOS UI
// ===============================
document.addEventListener("DOMContentLoaded", () => {
    const sendBtn = document.getElementById("send-btn");
    const userInput = document.getElementById("user-input");

    if (sendBtn) {
        sendBtn.addEventListener("click", sendMessage);
    }

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

// =======================
// GENERADOR (futuro)
// =======================
function abrirGenerador() {
    // Usamos el enlace oculto del index
    const link = document.getElementById("btn-generador");

    if (!link) {
        console.warn("[Nova] Botón oculto del generador no encontrado todavía.");
        return;
    }

    // Redirigir a la página del generador
    window.location.href = link.href;
}

// ======================================
// ATAJO PRIVADO (Ctrl + G) PARA ABRIR EL GENERADOR
// ======================================
document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === "g") {
        console.warn("[Nova&Pablo] Llave maestra activada → generador.html");
        abrirGenerador();
    }
});
