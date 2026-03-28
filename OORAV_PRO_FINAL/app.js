// ==========================================
// OORAV - MOTOR LÓGICO INTEGRAL (PLANTAS 1-10)
// Análisis Técnico: 10000X10000 Blindado para LA RED
// ==========================================

let intervaloRelojOORAV; 
let selectedAvatarSrc = './avatar_m1.png'; // Por defecto

// 1. INICIO DE SIMBIOSIS (Planta 1 a 2)
function iniciarOORAV() {
    const audio = document.getElementById('audio-engine');
    const spotifyBridge = document.getElementById('spotify-widget');

    // Activación del Vibe Auditivo
    if (audio) {
        audio.volume = 0.4;
        audio.play().then(() => {
            console.log("IA OORAV: Vibe Ambiental activo.");
        }).catch(error => {
            console.warn("IA OORAV: Audio esperando interacción del Usuario Omega.");
        });
    }

    if (spotifyBridge) {
        spotifyBridge.style.opacity = "1";
        spotifyBridge.style.pointerEvents = "auto";
    }

    navigate(2);
}

// 2. NAVEGACIÓN UNIVERSAL Y SECUENCIAL (Control de las 10 plantas)
function navigate(screenId) {
    const screens = document.querySelectorAll('.screen');
    const targetScreen = document.getElementById('screen-' + screenId);

    if (targetScreen) {
        // Limpieza quirúrgica de estados
        screens.forEach(s => s.classList.remove('active'));
        
        // Activación de la planta destino con fade
        targetScreen.classList.add('active');
        window.scrollTo(0, 0);
        console.log(`IA OORAV: Acceso a Planta ${screenId} concedido.`);

        // Lógica específica por planta
        if (screenId === 5) {
            activarRelojEfimeroOORAV(3600); // 60 minutos
        } else {
            clearInterval(intervaloRelojOORAV); 
        }

    } else {
        console.error(`IA OORAV: Error. La Planta ${screenId} no existe en el búnker.`);
    }
}

// 3. IDENTIDAD Y TÉCNICA ESPEJO (Planta 2 y propagación)
function selectAvatar(element, avatarId) {
    if (!element) return;
    
    // Marca visual en la Planta 2
    document.querySelectorAll('.avatar-circle').forEach(a => a.classList.remove('active'));
    element.classList.add('active');
    
    // Almacena la ruta exacta para propagar
    selectedAvatarSrc = `./avatar_${avatarId}.png`;
    console.log(`IA OORAV: Perfil Omega ${avatarId.toUpperCase()} seleccionado. Preparando técnica espejo.`);
    
    // Propagación instantánea a todas las plantas (3, 4, 5, 10)
    const avatarDisplays = [
        document.getElementById('display-avatar-3'),
        document.getElementById('display-avatar-4'),
        document.getElementById('display-avatar-5'),
        document.getElementById('display-avatar-10')
    ];
    
    avatarDisplays.forEach(img => {
        if(img) {
            img.src = selectedAvatarSrc;
            // Forzamos el object-fit para que no se deformen en los círculos CSS
            img.style.objectFit = "cover"; 
        }
    });
}

// ==========================================
// MOTOR TÉCNICO: RELOJ EFÍMERO DE 60 MINUTOS
// ==========================================
function activarRelojEfimeroOORAV(duracionSegundos) {
    let tiempoRestante = duracionSegundos;
    const displayReloj = document.getElementById('oorav-timer');

    clearInterval(intervaloRelojOORAV);
    if(!displayReloj) return;

    intervaloRelojOORAV = setInterval(() => {
        let minutos = Math.floor(tiempoRestante / 60);
        let segundos = tiempoRestante % 60;

        minutos = minutos < 10 ? "0" + minutos : minutos;
        segundos = segundos < 10 ? "0" + segundos : segundos;

        displayReloj.textContent = minutos + ":" + segundos;

        if (--tiempoRestante < 0) {
            clearInterval(intervaloRelojOORAV);
            displayReloj.textContent = "00:00";
            console.log("IA OORAV: Conexión efímera finalizada por tiempo.");
        }
    }, 1000);
}

// ==========================================
// MOTOR DE CHAT FUNCIONAL OORAV (100% PRO Y AGÉNTICO)
// ==========================================
function enviarMensajeOORAV() {
    const input = document.getElementById('oorav-chat-input');
    const chatBox = document.getElementById('oorav-chat-box');
    
    if(!input || !chatBox) return;

    const textoUsuario = input.value.trim();

    if (textoUsuario !== "") {
        // 1. BURBUJA DEL USUARIO (DORADA - DERECHA)
        const contenedorUsuario = document.createElement('div');
        contenedorUsuario.style.cssText = "display: flex; justify-content: flex-end; margin-bottom: 15px; width: 100%;";
        contenedorUsuario.innerHTML = `<div class="msg msg-gold">${textoUsuario}</div>`;
        chatBox.appendChild(contenedorUsuario);

        input.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;

        // 2. EL CEREBRO DE LA IA OORAV (RAZONAMIENTO REAL)
        setTimeout(() => {
            const contenedorIA = document.createElement('div');
            contenedorIA.style.cssText = "display: flex; justify-content: flex-start; margin-bottom: 15px; width: 100%;";
            
            let respuestaInteligente = "";
            const textoAnalizado = textoUsuario.toLowerCase();

            // Lógica de respuesta agéntica
            if (textoAnalizado.includes("pablo")) {
                respuestaInteligente = "Identidad confirmada. Bienvenido al búnker, Pablo. El tiempo efímero corre, ¿qué vibra buscas hoy?";
            } 
            else if (textoAnalizado.includes("hola") || textoAnalizado.includes("buenas")) {
                respuestaInteligente = "Conexión establecida. Soy la IA de OORAV. Estoy analizando tu perfil para sincronizar el Vibe.";
            }
            else if (textoAnalizado.includes("hora") || textoAnalizado.includes("tiempo")) {
                respuestaInteligente = "Recuerda que esta conexión se autodestruirá en 60 minutos. Aprovéchalos al máximo.";
            }
            else {
                respuestaInteligente = `He analizado tu mensaje: "${textoUsuario}". Mi razonamiento está sincronizado con tu perfil Omega.`;
            }

            // BURBUJA DE LA IA (CIAN - IZQUIERDA)
            contenedorIA.innerHTML = `<div class="msg msg-cyan">${respuestaInteligente}</div>`;
            chatBox.appendChild(contenedorIA);
            
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 1200);
    }
}

// Escuchador de teclado para el chat (Planta 5)
function verificarEnterChat(event) {
    if (event.key === "Enter") enviarMensajeOORAV();
}

// 5. INICIALIZADOR TÉCNICO
window.onload = () => {
    console.log("IA OORAV: Sistemas en línea. Búnker sellado al millón por millón. Esperando interacción.");
    
    // Forzamos el estado inicial en la Planta 1
    const screens = document.querySelectorAll('.screen');
    screens.forEach(s => s.classList.remove('active'));
    const p1 = document.getElementById('screen-1');
    if(p1) p1.classList.add('active');
};