// =====================
// Funciones de ayuda
// =====================

// Añadir un mensaje al chat visual
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

    // Desplaza hacia abajo automáticamente
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// =====================
// Enviar mensaje al backend
// =====================

async function sendMessage() {
    const input = document.getElementById("user-input");
    const text = input.value.trim();

    if (text === "") return;

    // Añadir mensaje del usuario al chat
    addMessage(text, "user");
    input.value = "";

    try {
        const response = await fetch("https://programanova-producción-f768.up.railway.app/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ mensaje: text })
        });

        const data = await response.json();

        // --- Normalizamos los datos que vienen del backend ---
        // Emoción e intención con valores seguros
        const emocion = data.emocion || "—";
        const intencion = data.intencion || "desconocida";

        // Resumen: puede venir como string o como objeto { resumen: "..." }
        let resumenTexto = "";
        if (data.resumen) {
            if (typeof data.resumen === "string") {
                resumenTexto = data.resumen;
            } else if (data.resumen.resumen) {
                resumenTexto = data.resumen.resumen;
            } else {
                // Último recurso: lo convertimos a texto
                resumenTexto = JSON.stringify(data.resumen);
            }
        }

        // --- Mostramos la respuesta principal de la IA en el chat ---
        addMessage(data.respuesta || "No he podido generar una respuesta.", "bot");

        // --- Mostramos el resumen como mensaje separado (si existe) ---
        if (resumenTexto) {
            addMessage("📌 Resumen: " + resumenTexto, "bot");
        }

        // --- Actualizamos el panel lateral ---
        document.getElementById("emotion-value").innerText = emocion;
        document.getElementById("intent-value").innerText = intencion;

        // Aquí usamos la hora local como “última actualización”
        const ahora = new Date().toLocaleString();
        document.getElementById("time-value").innerText = ahora;

    } catch (error) {
        addMessage("⚠️ Error conectando con el servidor.", "bot");
        console.error(error);
    }
}

// =====================
// Eventos
// =====================

const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-input");

// Click en el botón
sendBtn.addEventListener("click", (e) => {
    e.preventDefault(); // por si algún día está dentro de un formulario
    sendMessage();
});

// Enter en el input
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        e.preventDefault(); // evita que el navegador intente enviar formularios
        sendMessage();
    }
});

console.log("Frontend listo y escuchando eventos
