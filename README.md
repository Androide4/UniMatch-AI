# UniMatch-AI
# UniMatch AI - Sistema Inteligente de Recomendación de Universidades

## 📖 Descripción del Proyecto

UniMatch AI es un sistema basado en Inteligencia Artificial diseñado para analizar planes de estudio universitarios (pensum) en formato PDF y recomendar universidades según los intereses académicos del usuario.

El sistema utiliza procesamiento de lenguaje natural (NLP), embeddings y búsqueda semántica para comparar materias, enfoques académicos y contenidos curriculares entre diferentes universidades de Colombia.

Los documentos PDF son almacenados en una carpeta interna del proyecto y el chatbot consulta automáticamente esa base documental para responder preguntas en lenguaje natural.

---

# 🎯 Funcionalidades Principales

* Lectura automática de PDFs universitarios
* Extracción y limpieza de texto
* Generación de embeddings semánticos
* Almacenamiento vectorial con ChromaDB
* Comparación entre pensum universitarios
* Recomendaciones académicas mediante chatbot
* Interfaz conversacional con Streamlit

---

# 🛠️ Tecnologías Utilizadas

| Tecnología            | Uso                      |
| --------------------- | ------------------------ |
| Python                | Lenguaje principal       |
| PyMuPDF               | Extracción de texto PDF  |
| Sentence Transformers | Generación de embeddings |
| ChromaDB              | Base de datos vectorial  |
| Groq API              | Modelo LLM               |
| Streamlit             | Interfaz del chatbot     |

---

# 📋 Requisitos Previos

Antes de ejecutar el proyecto necesitas:

* Python 3.11 o superior
* pip
* Cuenta y API Key de Groq

Groq API:
https://console.groq.com

---

# 🚀 Instalación del Proyecto

## 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd unimatch_ai
```

---

## 2. Crear entorno virtual

### Linux / Mac

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

---

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
GROQ_API_KEY=tu_api_key_aqui

# Rutas del Proyecto
DATA_FOLDER=./data
VECTORSTORE_FOLDER=./vectorstore

# Configuración de Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# Configuración de ChromaDB
CHROMA_COLLECTION_NAME=unimatch_universidades

# Configuración de Groq LLM
GROQ_MODEL_NAME=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.4
GROQ_MAX_TOKENS=1024

# Debug
DEBUG=True
```

⚠️ Importante:
Nunca subir el archivo `.env` a GitHub.

---

## 5. Agregar PDFs

Crear la carpeta:

```bash
data/
```

Agregar los PDFs universitarios dentro de ella:

```bash
data/
├── universidad_a.pdf
├── universidad_b.pdf
└── universidad_c.pdf
```

---

# 📦 Estructura del Proyecto

```bash
unimatch_ai/
│
├── data/
│
├── app/
│   ├── pdf_manager.py
│   ├── pdf_extractor.py
│   ├── embedding_generator.py
│   ├── vector_retriever.py
│   ├── query_engine.py
│   └── chatbot.py
│
├── vectorstore/
│
├── streamlit_app.py
├── requirements.txt
├── .env
└── README.md
```

---

# ▶️ Ejecución del Proyecto

Ejecutar la interfaz del chatbot:

```bash
streamlit run streamlit_app.py
```

Luego abrir en el navegador:

```bash
http://localhost:8501
```

---

# 🔄 Flujo del Sistema

1. El sistema lee automáticamente los PDFs desde `/data`
2. Se extrae y limpia el texto
3. El contenido se divide en fragmentos
4. Se generan embeddings semánticos
5. Los embeddings se almacenan en ChromaDB
6. El usuario realiza una consulta
7. El sistema busca fragmentos relevantes
8. El chatbot genera una recomendación basada en los documentos

---

# 💬 Ejemplo de Consulta

Usuario:

```text
¿Qué universidad tiene mejor enfoque en desarrollo de software para Ingeniería de Sistemas?
```

Respuesta esperada:

```text
La Universidad A presenta un mayor enfoque en desarrollo de software debido a materias como Ingeniería de Software, Bases de Datos Avanzadas y Arquitectura de Sistemas.
```

---

# 📚 requirements.txt

```txt
# ============================================================
# UniMatch AI - Requirements
# Compatible con Python 3.11+ (sin versiones fijas)
# ============================================================

# PDF Processing
PyMuPDF
pdfplumber

# Embeddings & ML
sentence-transformers
torch

# Vector Database
chromadb

# LLM API
groq

# Frontend
streamlit

# Utilities
python-dotenv
numpy
pandas
tqdm
```

---

# 🐛 Troubleshooting

## Error: "No module named 'groq'"

```bash
pip install groq
```

---

## Error: "No PDFs found"

Verificar:

* existencia de la carpeta `/data`
* presencia de archivos PDF válidos

---

## Error: "GROQ_API_KEY not found"

Verificar:

* archivo `.env`
* API Key válida
* variables correctamente escritas

---

# 👨‍💻 Autores

* Eider Stiven Guerrero Acosta
* Deiby Santiago Montenegro Bahamón
* David Santiago Piñeros Niño

Proyecto académico enfocado en Inteligencia Artificial, NLP y búsqueda semántica de documentos universitarios.