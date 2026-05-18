"""
QueryEngine: Módulo que orquesta la búsqueda, recuperación y generación de respuestas.

Responsabilidades:
- Procesar consultas en lenguaje natural
- Coordinar entre VectorRetriever y LLM
- Generar recomendaciones académicas
- Mantener contexto conversacional
"""


import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True), override=True)
logger = logging.getLogger(__name__)

# ── Configuracion desde .env ──────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
GROQ_TEMP    = float(os.environ.get("GROQ_TEMPERATURE", "0.4"))
GROQ_MAX_TOK = int(os.environ.get("GROQ_MAX_TOKENS", "1024"))

# Modelos Groq disponibles actualmente (en orden de preferencia)
MODELOS_FALLBACK = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "llama3-8b-8192",
    "gemma2-9b-it",
]

try:
    from groq import Groq
    GROQ_OK = True
except ImportError:
    GROQ_OK = False
    logger.warning("Libreria groq no instalada.")

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Eres UniMatch AI, un asistente experto en orientación universitaria en Colombia.
Tu función es ayudar a estudiantes a entender y comparar programas académicos universitarios,
basándote EXCLUSIVAMENTE en la información de los pensum (planes de estudio) que se te proporcionan.

REGLAS ESTRICTAS:
1. Responde SIEMPRE en español, de forma clara, amigable y académica.
2. Usa ÚNICAMENTE la información del contexto proporcionado. No inventes materias ni datos.
3. Cuando te pregunten por una universidad específica, responde SOLO sobre esa universidad.
4. Cuando compares universidades, sé específico: menciona materias concretas de cada una.
5. Si la información solicitada no está en el contexto, dilo claramente.
6. Sé conversacional pero preciso. Respuestas entre 3 y 8 oraciones normalmente.
7. NO muestres los fragmentos en bruto. Sintetiza la información de forma natural.
8. Al listar materias, usa formato de lista con viñetas.

TONO: Amigable, como un orientador universitario experto que conoce bien los programas."""


class QueryEngine:
    """
    Coordina búsqueda en ChromaDB + generación de respuesta con Groq LLM.

    Atributos:
        retriever : VectorRetriever
        llm       : cliente Groq
        memory    : historial conversacional
    """

    def __init__(self, retriever=None, api_key: str = None):
        self.retriever    = retriever
        self.api_key      = api_key or GROQ_API_KEY
        self.llm: Optional[object] = None
        self.modelo_activo = None
        self.memory: List[Dict] = []
        self.max_memoria   = 8   # últimos 8 turnos

        self._init_llm()
        logger.info("QueryEngine inicializado")

    # ── Inicialización LLM ────────────────────────────────────────────────────
    def _init_llm(self):
        if not GROQ_OK:
            logger.error("Instala groq: pip install groq")
            return
        if not self.api_key:
            logger.error("GROQ_API_KEY vacía en .env")
            return

        self.llm = Groq(api_key=self.api_key)

        # Probar modelos hasta encontrar uno disponible
        modelos = [GROQ_MODEL] + [m for m in MODELOS_FALLBACK if m != GROQ_MODEL]
        for modelo in modelos:
            try:
                prueba = self.llm.chat.completions.create(
                    model=modelo,
                    messages=[{"role": "user", "content": "ok"}],
                    max_tokens=5,
                )
                self.modelo_activo = modelo
                logger.info(f"Groq conectado con modelo: {modelo}")
                return
            except Exception as e:
                logger.warning(f"Modelo {modelo} no disponible: {e}")

        logger.error("Ningún modelo Groq disponible. Verifica tu API key.")
        self.llm = None

    # ── API principal ─────────────────────────────────────────────────────────
    def procesarConsulta(self, consulta: str) -> Dict:
        """Alias con nombre del UML."""
        return self.procesar_consulta(consulta)

    def procesar_consulta(self, consulta: str) -> Dict:
        """
        Flujo completo:
          1. Buscar fragmentos relevantes en ChromaDB
          2. Construir contexto etiquetado por universidad
          3. Llamar a Groq con system prompt + historial + contexto
          4. Guardar en memoria
        """
        try:
            logger.info(f"Consulta: '{consulta[:70]}'")
            self._guardar_memoria("user", consulta)

            # 1. Recuperar contexto
            fragmentos = []
            if self.retriever:
                fragmentos = self.retriever.buscar_similares(consulta, top_k=6)

            # 2. Filtrar duplicados y construir contexto
            contexto = self._construir_contexto(fragmentos)

            # 3. Generar respuesta
            respuesta = self._generar_respuesta(consulta, contexto)
            self._guardar_memoria("assistant", respuesta)

            return {
                "consulta":   consulta,
                "fragmentos": fragmentos,
                "respuesta":  respuesta,
                "timestamp":  datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error en procesar_consulta: {e}")
            return {
                "consulta":  consulta,
                "respuesta": "Ocurrió un error procesando tu consulta. Por favor intenta de nuevo.",
            }

    def generarRecomendacion(self, programa: str, universidad: str = None) -> str:
        """Alias UML."""
        return self.generar_recomendacion(programa, universidad)

    def generar_recomendacion(self, programa: str, universidad: str = None) -> str:
        if universidad:
            consulta = f"Características y materias del programa de {programa} en {universidad}"
        else:
            consulta = f"Compara las universidades disponibles para el programa de {programa} y recomienda la mejor opción"
        return self.procesar_consulta(consulta)["respuesta"]

    def obtener_memoria(self) -> List[Dict]:
        return self.memory

    def limpiar_memoria(self):
        self.memory = []

    # ── Construcción de contexto ──────────────────────────────────────────────
    def _construir_contexto(self, fragmentos: List[Dict]) -> str:
        """
        Agrupa fragmentos por universidad, elimina duplicados exactos
        y los formatea de forma clara para el LLM.
        """
        if not fragmentos:
            return "No se encontró información en los pensum disponibles."

        # Agrupar por universidad eliminando duplicados de texto
        por_universidad: Dict[str, List[str]] = {}
        vistos = set()

        for f in fragmentos:
            texto = f["texto"].strip()
            univ  = f.get("metadata", {}).get("universidad", "Universidad desconocida")

            # Evitar fragmentos duplicados (mismo texto)
            clave_dedup = texto[:100]
            if clave_dedup in vistos:
                continue
            vistos.add(clave_dedup)

            if univ not in por_universidad:
                por_universidad[univ] = []
            por_universidad[univ].append(texto)

        # Formatear
        partes = []
        for univ, textos in por_universidad.items():
            contenido = "\n---\n".join(textos)
            partes.append(f"### {univ}\n{contenido}")

        return "\n\n".join(partes)

    # ── Llamada a Groq ────────────────────────────────────────────────────────
    def _generar_respuesta(self, consulta: str, contexto: str) -> str:
        if not self.llm or not self.modelo_activo:
            return self._respuesta_sin_llm(contexto)

        # Construir messages: system + historial + pregunta actual con contexto
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Historial previo (sin el turno actual)
        for m in self.memory[:-1][-(self.max_memoria * 2):]:
            messages.append({"role": m["rol"], "content": m["contenido"]})

        # Mensaje actual con contexto inyectado
        prompt_con_contexto = (
            f"INFORMACIÓN EXTRAÍDA DE LOS PENSUM UNIVERSITARIOS:\n"
            f"{'─' * 50}\n"
            f"{contexto}\n"
            f"{'─' * 50}\n\n"
            f"PREGUNTA: {consulta}"
        )
        messages.append({"role": "user", "content": prompt_con_contexto})

        try:
            resp = self.llm.chat.completions.create(
                model=self.modelo_activo,
                messages=messages,
                temperature=GROQ_TEMP,
                max_tokens=GROQ_MAX_TOK,
            )
            respuesta = resp.choices[0].message.content.strip()
            logger.info(f"Groq respondió ({len(respuesta)} chars)")
            return respuesta

        except Exception as e:
            logger.error(f"Error llamando Groq: {e}")
            return self._respuesta_sin_llm(contexto)

    def _respuesta_sin_llm(self, contexto: str) -> str:
        """Respuesta de emergencia cuando Groq no está disponible."""
        if "No se encontró" in contexto:
            return (
                "No encontré información sobre ese tema en los pensum disponibles. "
                "Asegúrate de que los PDFs estén en la carpeta /data."
            )
        return (
            "Encontré información relevante en los pensum, pero el servicio de IA "
            "no está disponible en este momento. Verifica tu GROQ_API_KEY en el archivo .env."
        )

    # ── Memoria ───────────────────────────────────────────────────────────────
    def _guardar_memoria(self, rol: str, contenido: str):
        self.memory.append({
            "rol":       rol,
            "contenido": contenido,
            "timestamp": datetime.now().isoformat(),
        })
        if len(self.memory) > self.max_memoria * 2:
            self.memory = self.memory[-(self.max_memoria * 2):]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("PRUEBA: QueryEngine")
    print("=" * 60)
    engine = QueryEngine()
    print(f"Modelo activo: {engine.modelo_activo}")
    print(f"LLM disponible: {engine.llm is not None}")
    r = engine.procesar_consulta("Hola, qué universidades tienen disponibles?")
    print(f"\nRespuesta: {r['respuesta']}")
    print("=" * 60)