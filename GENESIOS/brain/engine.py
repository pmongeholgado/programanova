from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import multiprocessing

class GenerativeBrain:
    def __init__(self, model_path: str):
        # 1. Verificación de seguridad del 'Cerebro'
        if not os.path.exists(model_path):
            print(f"ERROR CRÍTICO: No se encuentra el motor en {model_path}")
            raise FileNotFoundError("Falta el archivo llm-local.bin en brain/modelos/")

        print(f"--- Iniciando el núcleo OORAV con el modelo: {os.path.basename(model_path)} ---")
        
        # 2. Configuración técnica optimizada para la red
        self.llm = LlamaCpp(
            model_path=model_path,
            temperature=0.8,       # Un toque más de creatividad para mimetizar mejor
            max_tokens=512,       # Permitimos respuestas con más sustancia si es necesario
            n_ctx=2048,           # Memoria de corto plazo expandida
            n_threads=multiprocessing.cpu_count(), # Usa toda la potencia de tu PC
            verbose=False,
            f16_kv=True           # Optimización de memoria para mayor velocidad
        )
        print("Simbiosis motor-hardware completada con éxito.")

    def generate_response(self, context: str, user_input: str) -> str:
        # 3. El Prompt Maestro: Configurado para el público 20-35 años
        # Aquí es donde ocurre la 'Duplicación' de comportamiento
        template = """
        SISTEMA DE IDENTIDAD OORAV: Eres un agente digital de vanguardia.
        Tu estilo es directo, humano, sin protocolos robóticos y con alta inteligencia social.
        
        CONTEXTO DE MEMORIA (Lo que ya sabes): 
        {context}
        
        ENTRADA DEL USUARIO: 
        {user_input}
        
        INSTRUCCIÓN: Responde de forma orgánica. Si el contexto muestra un patrón, duplícalo.
        RESPUESTA:
        """
        
        prompt = PromptTemplate(
            template=template, 
            input_variables=["context", "user_input"]
        )
        
        # 4. Ejecución de la cadena generativa
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            # Limpiamos la respuesta de espacios innecesarios
            response = chain.run(context=context, user_input=user_input)
            return response.strip()
        except Exception as e:
            return f"Error en la generación: {str(e)}"

if __name__ == "__main__":
    print("Módulo de cerebro (engine.py) verificado para la red.")