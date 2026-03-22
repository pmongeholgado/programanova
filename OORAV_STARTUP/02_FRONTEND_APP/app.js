// ==========================================
// OORAV - MOTOR LÓGICO INTEGRAL (PLANTAS 1-10)
// Análisis Técnico: 10000X10000 Blindado para LA RED
// ==========================================

// 1. INICIO DE SIMBIOSIS (Planta 1)
function startSimbiosis() {
    const audio = document.getElementById('audio-engine');
    const spotifyBridge = document.getElementById('external-music-bridge');

    // Activación del Vibe Auditivo
    if (audio) {
        audio.volume = 0.4; // Volumen balanceado para no saturar
        audio.play().then(() => {
            console.log("IA OORAV: Vibe Ambiental activo.");
        }).catch(error => {
            console.warn("IA OORAV: Audio esperando permiso del Usuario Omega.");
        });
    }

    // Suavizamos la aparición del puente de música
    if (spotifyBridge) {
        spotifyBridge.style.opacity = "1";
    }

    // Salto a la Planta 2
    navigate(2);
}

// 2. NAVEGACIÓN UNIVERSAL (Control de las 10 plantas)
function navigate(screenId) {
    const screens = document.querySelectorAll('.screen');
    const targetScreen = document.getElementById('screen-' + screenId);

    if (targetScreen) {
        // Limpieza quirúrgica de estados anteriores
        screens.forEach(s => {
            s.classList.remove('active');
            s.style.display = 'none'; // Blindaje extra para evitar solapamientos
        });

        // Activación de la planta destino
        targetScreen.style.display = 'flex'; // Aseguramos el layout
        setTimeout(() => {
            targetScreen.classList.add('active');
        }, 10);

        // Reset de scroll y Log de estado
        window.scrollTo(0, 0);
        console.log(`IA OORAV: Acceso a Planta ${screenId} concedido.`);
        
        // AMPLIACIÓN OORAV: Técnica Espejo al confirmar Planta 3
        if (screenId == 3) {
            const avatarActivo = document.querySelector('.avatar-circle.active img');
            const siluetaActual = document.querySelector('.omega-silhouette');
            
            if (avatarActivo && siluetaActual) {
                const nuevaImagen = document.createElement('img');
                nuevaImagen.src = avatarActivo.src;
                nuevaImagen.className = 'omega-silhouette';
                nuevaImagen.style.borderRadius = '50%';
                nuevaImagen.style.objectFit = 'cover';
                
                siluetaActual.parentNode.replaceChild(nuevaImagen, siluetaActual);
            }
        }
    } else {
        console.error(`IA OORAV: Error de ruta. La Planta ${screenId} es inaccesible.`);
    }
}

// 3. IDENTIDAD (Planta 2 y Reflejo a Planta 3)
function selectAvatar(element) {
    if (element) {
        // 1. Marca el avatar como activo en el búnker de la Planta 2
        document.querySelectorAll('.avatar-circle').forEach(a => a.classList.remove('active'));
        element.classList.add('active');

        // 2. TÉCNICA ESPEJO: Captura la foto y la proyecta al instante en la Planta 3
        const fotoSeleccionada = element.querySelector('img').src;
        const espejoOmega = document.querySelector('.omega-silhouette'); 
        
        if (espejoOmega) {
            espejoOmega.src = fotoSeleccionada;
            // Blindaje estético para que la foto encaje perfecta en el anillo dual
            espejoOmega.style.objectFit = 'cover';
            espejoOmega.style.borderRadius = '50%';
        }

        console.log("IA OORAV: Perfil Omega actualizado y Técnica Espejo sincronizada al 100%.");
    }
}

// ==========================================
// 4. FUNCIONALIDAD PORTADA 5 (Inyección Exclusiva LA RED)
// ==========================================

function activarRadarOorav() {
    console.log("IA OORAV: Radar presionado. Escaneando zona local...");
    // Efecto visual previo al salto (se puede enlazar con animaciones CSS)
    const radarBtn = document.getElementById('btn-radar-p5');
    if(radarBtn) radarBtn.classList.add('radar-scanning');
    
    // Transición segura y directa a la Portada 6 tras 1.5 segundos
    setTimeout(() => {
        navigate(6);
    }, 1500);
}

function accionAnagrama(numero) {
    console.log(`IA OORAV: Anagrama inferior ${numero} activado.`);
    
    // Asignación de rutas para los 3 anagramas de la Portada 5
    if (numero === 1) {
        // Lógica del anagrama 1
        console.log("Procesando comando Anagrama 1...");
    } else if (numero === 2) {
        // Lógica del anagrama 2
        console.log("Procesando comando Anagrama 2...");
    } else if (numero === 3) {
        // Lógica del anagrama 3 (Ejemplo: Salto manual a la 6)
        navigate(6);
    }
}

// ==========================================
// 5. MONETIZACIÓN PRO (Planta 8)
// ==========================================
function selectTier(element) {
    if (element) {
        document.querySelectorAll('.pricing-tier').forEach(t => t.classList.remove('active-tier'));
        element.classList.add('active-tier');
        console.log("IA OORAV: Nivel de suscripción seleccionado.");
    }
}

// ==========================================
// 6. CULMINACIÓN E INFORME (Planta 10)
// ==========================================
function downloadReport() {
    const btnDescarga = document.getElementById('btn-descarga');
    if (!btnDescarga) return;
    
    // Feedback visual premium al estilo OORAV
    btnDescarga.innerHTML = "GENERANDO...<br>ESPÍRITU OMEGA";
    btnDescarga.disabled = true; // Evitamos duplicidad de procesos
    
    // Simulación de proceso de IA
    setTimeout(() => {
        btnDescarga.innerHTML = "INFORME GUARDADO<br>EN TU BÚNKER";
        btnDescarga.style.background = "linear-gradient(135deg, rgba(212,175,55,0.6), rgba(0,243,255,0.3))";
        btnDescarga.style.borderColor = "#fff";
        btnDescarga.style.boxShadow = "0 0 30px rgba(212,175,55,0.7)";
        
        alert("¡Vibe Match completado, Usuario Omega! Tu informe PRO ha sido descargado. Bienvenido oficialmente a la cúspide de OORAV.");
        console.log("IA OORAV: Operación finalizada con éxito.");
    }, 1500);
}

// 7. INICIALIZADOR TÉCNICO (Blindaje de arranque RED)
window.onload = () => {
    console.log("IA OORAV: Sistemas en línea. Esperando al Usuario Omega.");
    // Aseguramos que solo la planta 1 esté visible al entrar a la web
    const initialScreen = document.querySelector('.screen.active');
    if(!initialScreen) {
        navigate(1);
    }
};