const API_URL = "https://programanovabackend-production.up.railway.app/chat"; // <--- AQUÍ TU URL EXACTA

async function enviarMensaje() {
    const input = document.getElementById("mensajeUsuario");
    const mensaje = input.value.trim();

    if (!mensaje) return;

    try {
        const respuesta = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ mensaje })
        });

        const data = await respuesta.json();

        document.getElementById("resultado").innerText =
            `🧠 Nova responde:\n${data.respuesta}\n\n📌 Resumen: ${data.resumen}`;

    } catch (error) {
        document.getElementById("resultado").innerText =
            "⚠️ Error al conectar con el backend.";
    }

    input.value = "";
}
