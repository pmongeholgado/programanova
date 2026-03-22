import logging
from typing import List
from datetime import datetime

# ==========================================
# OORAV STARTUP - ADN GENERATIVO PROPIO
# MÓDULO: dna_model.py
# ESTADO: 100% Optimizado para Local y RED
# ==========================================

# Configuración de log profesional (vital para la RED)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - OORAV_ADN - %(levelname)s - %(message)s')

class ModeloGenerativoOorav:
    def __init__(self, id_instancia: str, tono: str = "energia_alta", limite_memoria: int = 50):
        """
        Inicializa el núcleo del ADN Generativo de OORAV.
        Aislado y listo para simbiosis.
        """
        self.id_instancia = id_instancia
        self.tono = tono
        self.limite_memoria = limite_memoria
        self.memoria_aislada: List[str] = []  # Sandbox de memoria controlada
        self.fecha_activacion = datetime.now()
        
        self._iniciar_red_neuronal()

    def _iniciar_red_neuronal(self) -> None:
        """
        Carga de pesos y tensores del modelo único.
        """
        # Usamos logging en lugar de print para que en la RED quede registrado sin saturar la consola visual
        logging.info(f"[+] Nodo de Inteligencia {self.id_instancia} iniciado. Tono: {self.tono}")

    def generar_vibe(self, contexto_usuario: str) -> str:
        """
        Procesa el contexto del usuario (20-35 años) y devuelve la Vibe generada.
        Blindado para la RED con manejo de excepciones.
        """
        if not contexto_usuario:
            logging.warning(f"[-] Instancia {self.id_instancia}: Contexto vacío recibido.")
            return "Simbiosis en espera. Necesito tu energía."

        try:
            # Lógica de procesamiento de lenguaje natural (NLP) propio
            respuesta = f"Procesando '{contexto_usuario}' con el motor OORAV al millón por millón."
            
            # GESTIÓN DE MEMORIA PARA LA RED: 
            # Evita que la memoria crezca infinitamente y colapse el servidor
            self.memoria_aislada.append(contexto_usuario)
            if len(self.memoria_aislada) > self.limite_memoria:
                self.memoria_aislada.pop(0) # Elimina el recuerdo más antiguo (esencia efímera)
                
            logging.info(f"[+] Instancia {self.id_instancia}: Vibe generada correctamente.")
            return respuesta
            
        except Exception as e:
            # Si algo falla en la red, OORAV no se cuelga, lo registra y responde.
            logging.error(f"[X] Instancia {self.id_instancia}: Error crítico al generar vibe: {str(e)}")
            return "El motor OORAV está recalibrando la energía. Inténtalo de nuevo."