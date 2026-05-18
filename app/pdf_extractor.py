"""
PdfExtractor: Módulo responsable de extraer y limpiar texto de PDFs.

Responsabilidades:
- Extraer texto de archivos PDF usando PyMuPDF
- Limpiar y normalizar el texto extraído
- Extraer metadata de los documentos
- Dividir contenido en secciones procesables
"""

"""
PdfExtractor: Extrae, limpia y fragmenta texto de archivos PDF.
"""

import re
import os
from pathlib import Path
from typing import Dict, List
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE",    500))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP",  50))

try:
    import fitz
    PYMUPDF_OK = True
except ImportError:
    PYMUPDF_OK = False
    logger.warning("PyMuPDF no disponible – usando fallback.")


class PdfExtractor:
    """Extractor de texto desde archivos PDF."""

    def __init__(self):
        self.texto_extraido: str = ""
        logger.info("PdfExtractor inicializado")

    def extraer_texto(self, ruta_pdf: str) -> str:
        try:
            logger.info(f"Extrayendo texto de: {ruta_pdf}")
            ruta = Path(ruta_pdf)
            if not ruta.exists():
                logger.error(f"Archivo no encontrado: {ruta_pdf}")
                return ""
            if PYMUPDF_OK:
                doc = fitz.open(str(ruta))
                paginas = []
                for i in range(len(doc)):
                    try:
                        paginas.append(doc[i].get_text())
                    except Exception as e:
                        logger.warning(f"Error en pagina {i}: {e}")
                doc.close()
                texto = "\n".join(paginas)
            else:
                raw = ruta.read_bytes()
                try:
                    texto = raw.decode("latin-1")
                except Exception:
                    texto = raw.decode("utf-8", errors="replace")
                texto = re.sub(r"[^\x20-\x7E\n]", " ", texto)
            self.texto_extraido = texto
            logger.info(f"Texto extraido: {len(texto)} caracteres")
            return texto
        except Exception as e:
            logger.error(f"Error extrayendo texto: {e}")
            return ""

    def limpiar_texto(self, texto: str) -> str:
        try:
            logger.info("Limpiando texto...")
            texto = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", texto)
            texto = re.sub(r" +", " ", texto)
            texto = re.sub(r"\n{2,}", "\n", texto)
            texto = "\n".join(l.strip() for l in texto.split("\n"))
            texto = "\n".join(l for l in texto.split("\n") if l.strip())
            texto = texto.strip()
            logger.info(f"Texto limpio: {len(texto)} caracteres")
            return texto
        except Exception as e:
            logger.error(f"Error limpiando: {e}")
            return texto

    def extraer_metadata(self, ruta_pdf: str) -> Dict:
        try:
            logger.info(f"Extrayendo metadata de: {ruta_pdf}")
            ruta = Path(ruta_pdf)
            if not ruta.exists():
                logger.error(f"No encontrado: {ruta_pdf}")
                return {}
            if PYMUPDF_OK:
                doc = fitz.open(str(ruta))
                meta = {
                    "titulo":         doc.metadata.get("title")  or ruta.stem.replace("_", " "),
                    "autor":          doc.metadata.get("author") or "Desconocido",
                    "paginas":        len(doc),
                    "tamano_bytes":   ruta.stat().st_size,
                    "nombre_archivo": ruta.name,
                    "ruta":           str(ruta_pdf),
                }
                doc.close()
            else:
                meta = {
                    "titulo":         ruta.stem.replace("_", " "),
                    "autor":          "Desconocido",
                    "paginas":        1,
                    "tamano_bytes":   ruta.stat().st_size,
                    "nombre_archivo": ruta.name,
                    "ruta":           str(ruta_pdf),
                }
            logger.info(f"Metadata lista: {meta['paginas']} pagina(s)")
            return meta
        except Exception as e:
            logger.error(f"Error en metadata: {e}")
            return {}

    def procesar_pdf_completo(self, ruta_pdf: str) -> Dict:
        logger.info(f"Procesando PDF completo: {ruta_pdf}")
        texto_bruto  = self.extraer_texto(ruta_pdf)
        texto_limpio = self.limpiar_texto(texto_bruto)
        metadata     = self.extraer_metadata(ruta_pdf)
        return {
            "metadata":          metadata,
            "texto_bruto":       texto_bruto,
            "texto_limpio":      texto_limpio,
            "longitud_original": len(texto_bruto),
            "longitud_limpia":   len(texto_limpio),
        }

    def dividir_en_fragmentos(
        self,
        texto: str,
        tamano_fragmento: int = CHUNK_SIZE,
        solapamiento:     int = CHUNK_OVERLAP,
    ) -> List[str]:
        """Divide texto en fragmentos garantizando avance siempre hacia adelante."""
        try:
            logger.info(f"Fragmentando ({len(texto)} chars, chunk={tamano_fragmento}, overlap={solapamiento})...")
            if not texto.strip():
                logger.warning("Texto vacio, sin fragmentos.")
                return []

            fragmentos: List[str] = []
            inicio = 0
            n = len(texto)

            while inicio < n:
                fin = min(inicio + tamano_fragmento, n)
                fragmento = texto[inicio:fin]

                # Cortar en limite de palabra solo si no es el ultimo trozo
                if fin < n:
                    pos = fragmento.rfind(" ")
                    if pos > 0:
                        fragmento = fragmento[:pos]
                        fin = inicio + pos

                if fragmento.strip():
                    fragmentos.append(fragmento.strip())

                # AVANCE GARANTIZADO: nunca retrocede
                nuevo_inicio = fin - solapamiento
                if nuevo_inicio <= inicio:
                    nuevo_inicio = fin          # saltar overlap si causaria loop
                inicio = nuevo_inicio

            logger.info(f"{len(fragmentos)} fragmentos generados")
            return fragmentos
        except Exception as e:
            logger.error(f"Error fragmentando: {e}")
            return []


if __name__ == "__main__":
    import sys
    print("\n" + "=" * 70)
    print("PRUEBA: PdfExtractor")
    print("=" * 70)

    ext = PdfExtractor()
    data_dir = Path("data")
    pdfs = sorted(data_dir.glob("*.pdf")) if data_dir.exists() else []

    if not pdfs:
        print("Sin PDFs en ./data")
        sys.exit(0)

    ruta = str(pdfs[0])
    print(f"\nPDF: {ruta}")

    meta = ext.extraer_metadata(ruta)
    print(f"\nMetadata: {meta}")

    texto = ext.extraer_texto(ruta)
    print(f"\nTexto ({len(texto)} chars): {texto[:150].strip()}...")

    limpio = ext.limpiar_texto(texto)
    print(f"\nLimpio: {len(limpio)} chars")

    frags = ext.dividir_en_fragmentos(limpio, tamano_fragmento=200, solapamiento=30)
    print(f"\nFragmentos: {len(frags)}")
    for i, f in enumerate(frags):
        print(f"  [{i+1}] {f[:80]}...")

    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70 + "\n")