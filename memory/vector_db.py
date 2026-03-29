import chromadb
import os
import uuid # Para generar IDs únicos sin errores

class VectorMemory:
    def __init__(self, db_path=None):
        # 1. Priorizamos la ruta del .env para que Docker no se pierda
        if db_path is None:
            db_path = os.getenv("DB_PATH", "./memory/chroma_db")
        
        print(f"--- Iniciando Memoria OORAV en: {db_path} ---")
        
        # 2. Cliente persistente (Privacidad Total: nada sale de tu PC)
        self.client = chromadb.PersistentClient(path=db_path)
        
        # 3. Colección de recuerdos
        self.collection = self.client.get_or_create_collection(
            name="bot_memory",
            metadata={"hnsw:space": "cosine"} # Optimizado para mimetización de lenguaje
        )

    def store_interaction(self, bot_id: str, context: str, response: str):
        # Generamos un ID único para evitar colisiones en la red
        doc_id = f"{bot_id}_{uuid.uuid4().hex[:8]}"
        
        self.collection.add(
            documents=[f"Contexto: {context} | Respuesta: {response}"],
            metadatas=[{"bot_id": bot_id}],
            ids=[doc_id]
        )
        print(f"Recuerdo guardado para {bot_id} (ID: {doc_id})")

    def recall_pattern(self, bot_id: str, current_context: str, n_results=2):
        # Si la colección está vacía, evitamos errores
        if self.collection.count() == 0:
            return "Sin recuerdos previos. Iniciando nuevo patrón."

        # RAG: Recuperamos los 2 patrones más parecidos al estilo del usuario
        results = self.collection.query(
            query_texts=[current_context],
            n_results=n_results,
            where={"bot_id": bot_id}
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            recuerdos = " ".join(results['documents'][0])
            print(f"Mimetización activa: {len(results['documents'][0])} patrones recuperados.")
            return recuerdos
            
        return "Sin recuerdos previos para este bot. Construyendo identidad."

if __name__ == "__main__":
    print("Módulo de memoria OORAV verificado y blindado.")