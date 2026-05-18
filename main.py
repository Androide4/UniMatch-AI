"""
main.py - Punto de entrada principal que integra todos los módulos de UniMatch AI.

Pipeline completo:
1. PdfManager: Lee PDFs desde /data/
2. PdfExtractor: Extrae y limpia texto
3. EmbeddingGenerator: Genera embeddings
4. VectorRetriever: Busca fragmentos similares
5. QueryEngine: Procesa consultas y genera respuestas
6. Chatbot: Interfaz conversacional con usuario
"""

"""
main.py - Pipeline completo de UniMatch AI.
IMPORTANTE: load_dotenv() va PRIMERO, antes de cualquier import local.
"""

# ── 1. Cargar .env ANTES de todo ─────────────────────────────────────────────
import os
from dotenv import load_dotenv

# Buscar .env en la misma carpeta que este archivo
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)

# ── 2. Verificar variables criticas inmediatamente ───────────────────────────
import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

_groq_key = os.environ.get("GROQ_API_KEY", "")
if _groq_key:
    logger.info(f"GROQ_API_KEY cargada correctamente: {_groq_key[:8]}...")
else:
    logger.warning("GROQ_API_KEY NO encontrada. Revisa tu archivo .env")

# ── 3. Ahora si importar modulos locales ─────────────────────────────────────
from pathlib import Path
from typing import List, Dict

from app.pdf_manager         import PdfManager
from app.pdf_extractor       import PdfExtractor
from app.embedding_generator import EmbeddingGenerator
from app.vector_retriever    import VectorRetriever
from app.query_engine        import QueryEngine
from app.chatbot             import Chatbot

# Configuracion desde .env
DATA_FOLDER        = os.environ.get("DATA_FOLDER",        "./data")
VECTORSTORE_FOLDER = os.environ.get("VECTORSTORE_FOLDER", "./vectorstore")
CHUNK_SIZE         = int(os.environ.get("CHUNK_SIZE",     500))
CHUNK_OVERLAP      = int(os.environ.get("CHUNK_OVERLAP",  50))
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY",       "")


class UnimatchAI:
    """Sistema completo UniMatch AI."""

    def __init__(self, limpiar_bd: bool = False):
        logger.info("=" * 60)
        logger.info("  INICIANDO UNIMATCH AI")
        logger.info("=" * 60)

        Path(DATA_FOLDER).mkdir(parents=True, exist_ok=True)
        Path(VECTORSTORE_FOLDER).mkdir(parents=True, exist_ok=True)

        logger.info("\n[1/6] PdfManager")
        self.pdf_manager = PdfManager(ruta_carpeta=DATA_FOLDER)

        logger.info("\n[2/6] PdfExtractor")
        self.pdf_extractor = PdfExtractor()

        logger.info("\n[3/6] EmbeddingGenerator")
        self.embedding_generator = EmbeddingGenerator()

        # Limpiar BD si se solicita (borra datos de prueba anteriores)
        if limpiar_bd:
            self._limpiar_coleccion()

        logger.info("\n[4/6] VectorRetriever")
        self.vector_retriever = VectorRetriever(self.embedding_generator)

        logger.info("\n[5/6] QueryEngine — conectando con Groq")
        self.query_engine = QueryEngine(
            retriever=self.vector_retriever,
            api_key=GROQ_API_KEY,
        )

        logger.info("\n[6/6] Chatbot")
        self.chatbot = Chatbot(query_engine=self.query_engine)

        logger.info("\n" + "=" * 60)
        logger.info("  SISTEMA LISTO")
        logger.info(f"  Groq activo : {self.query_engine.llm is not None}")
        logger.info(f"  Vectorstore : {self.embedding_generator.obtener_estadisticas()['vectorstore']}")
        logger.info("=" * 60 + "\n")

    # ── Limpieza de BD ────────────────────────────────────────────────────────
    def _limpiar_coleccion(self):
        """Elimina todos los documentos de la coleccion ChromaDB."""
        try:
            col = self.embedding_generator.coleccion
            if col and col.count() > 0:
                todos = col.get()
                if todos and todos["ids"]:
                    col.delete(ids=todos["ids"])
                    logger.info(f"BD limpiada: {len(todos['ids'])} documentos eliminados")
        except Exception as e:
            logger.warning(f"No se pudo limpiar la BD: {e}")

    # ── Indexacion ────────────────────────────────────────────────────────────
    def procesar_pdfs(self, forzar_reindexado: bool = False) -> bool:
        """
        Indexa todos los PDFs de /data/ en ChromaDB.
        Si forzar_reindexado=True, limpia primero la coleccion.
        """
        logger.info("\n=== PROCESANDO PDFs ===")

        if forzar_reindexado:
            self._limpiar_coleccion()

        pdfs = self.pdf_manager.cargar_pdfs()
        if not pdfs:
            logger.warning(f"Sin PDFs en '{DATA_FOLDER}'")
            return False

        total = 0
        for pdf in pdfs:
            logger.info(f"\n  PDF: {pdf.nombre}")

            resultado     = self.pdf_extractor.procesar_pdf_completo(pdf.ruta)
            texto_limpio  = resultado["texto_limpio"]

            if not texto_limpio.strip():
                logger.warning(f"  Sin texto — omitido")
                continue

            fragmentos = self.pdf_extractor.dividir_en_fragmentos(
                texto_limpio,
                tamano_fragmento=CHUNK_SIZE,
                solapamiento=CHUNK_OVERLAP,
            )

            if not fragmentos:
                logger.warning(f"  Sin fragmentos — omitido")
                continue

            # Extraer nombre de universidad del nombre del archivo
            stem   = Path(pdf.nombre).stem          # universidad_a_ingenieria_sistemas
            partes = stem.lower().split("_")
            # Buscar patron "universidad_X"
            nombre_univ = stem.replace("_", " ").title()  # fallback
            for i, p in enumerate(partes):
                if p == "universidad" and i + 1 < len(partes):
                    nombre_univ = f"Universidad {partes[i+1].upper()}"
                    break

            metadata = {
                "pdf":        pdf.nombre,
                "universidad": nombre_univ,
                "paginas":    str(resultado["metadata"].get("paginas", 1)),
            }

            ok = self.embedding_generator.almacenar_en_vectorstore(
                fragmentos, metadata, prefijo_id=stem
            )

            if ok:
                total += len(fragmentos)
                logger.info(f"  OK — {len(fragmentos)} fragmentos como '{nombre_univ}'")
            else:
                logger.error(f"  ERROR guardando {pdf.nombre}")

        logger.info(f"\n=== INDEXACION: {total} fragmentos totales ===\n")
        return total > 0

    # ── Chat ──────────────────────────────────────────────────────────────────
    def chatear(self, mensaje: str) -> str:
        r = self.chatbot.recibir_mensaje(mensaje)
        return r.get("respuesta", "Error procesando mensaje.")

    # ── Info ──────────────────────────────────────────────────────────────────
    def obtener_estadisticas(self) -> Dict:
        return {
            "pdfs_disponibles": self.pdf_manager.contar_pdfs(),
            "embeddings":       self.embedding_generator.obtener_estadisticas(),
            "sesion":           self.chatbot.obtener_contexto_sesion(),
            "groq_activo":      self.query_engine.llm is not None,
        }

    def obtener_historial_chat(self) -> List[Dict]:
        return self.chatbot.obtener_historial_sesion()


# ── Demo en consola ───────────────────────────────────────────────────────────
def main():
    sistema = UnimatchAI(limpiar_bd=True)   # limpiar_bd=True borra datos de prueba
    sistema.procesar_pdfs()

    stats = sistema.obtener_estadisticas()
    print(f"\nFragmentos en BD : {stats['embeddings'].get('total_documentos', 0)}")
    print(f"Groq activo      : {stats['groq_activo']}")

    preguntas = [
        "Hola!",
        "Cual es la mejor universidad para aprender a programar?",
        "Compara las universidades",
    ]
    for p in preguntas:
        print(f"\nUsuario: {p}")
        print(f"Bot    : {sistema.chatear(p)}")


if __name__ == "__main__":
    main()