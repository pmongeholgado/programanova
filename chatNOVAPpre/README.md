# chatNOVAP

chatNOVAP es un chat de inteligencia artificial desarrollado como parte del ecosistema **Programa Nova Presentaciones**.

El objetivo de chatNOVAP es ofrecer una experiencia de conversación donde la IA no solo responde preguntas, sino que **colabora con el usuario en el desarrollo de proyectos tecnológicos**.

Este proyecto forma parte de la iniciativa **NOVA & PABLO – Simbiosis Humano-IA**, donde se explora una nueva forma de interacción entre personas e inteligencia artificial.

---

# Arquitectura del proyecto

chatNOVAP está construido con una arquitectura simple y clara:

Frontend

* HTML
* CSS
* JavaScript

Backend

* Python
* FastAPI

Inteligencia Artificial

* OpenAI API

Persistencia de conversaciones

* JSON local

---

# Estructura del proyecto

```
chatNOVAP
│
├── backend
│   ├── main_novap.py
│   ├── routes_novap.py
│   ├── services_novap.py
│   ├── schemas_novap.py
│   ├── nova_identity.py
│   ├── memory_store.py
│   ├── persistence.py
│   └── config_novap.py
│
├── frontend
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── tests
│   └── test_health.py
│
├── requirements.txt
└── README.md
```

---

# Requisitos

Python 3.10 o superior

Instalar dependencias:

```
pip install -r requirements.txt
```

---

# Variables de entorno

Crear un archivo `.env` dentro de la carpeta `backend` con la clave de OpenAI:

```
OPENAI_API_KEY=tu_clave_aqui
```

Este archivo **no debe subirse a GitHub**.

---

# Ejecutar el proyecto en local

Iniciar el backend:

```
python -m uvicorn backend.main_novap:app --reload --port 8000
```

Backend disponible en:

```
http://127.0.0.1:8000
```

Documentación automática de la API:

```
http://127.0.0.1:8000/docs
```

Abrir el chat en el navegador:

```
frontend/index.html
```

---

# Endpoints principales

Health check

```
GET /novap/health
```

Chat con la IA

```
POST /novap/chat
```

Ejemplo de petición:

```
{
 "chat_id": "test",
 "message": "hola"
}
```

---

# Despliegue

Arquitectura recomendada:

Frontend
Netlify

Backend
Railway

El frontend se comunica con el backend mediante el endpoint:

```
/novap/chat
```

---

# Objetivo del proyecto

chatNOVAP busca explorar una nueva forma de interacción humano-IA basada en:

* colaboración
* acompañamiento en proyectos
* aprendizaje conjunto

La IA NOVA está diseñada para **ayudar a construir, no solo responder**.

---

# Licencia

Proyecto experimental dentro del ecosistema **Programa Nova Presentaciones**.

---

# Autores

Pablo Monge
NOVA (AI)

Proyecto desarrollado dentro de la iniciativa:

**Simbiosis Humano-IA**
