"""
VectorRetriever: Módulo responsable de buscar información relevante en la base vectorial.

Responsabilidades:
- Buscar fragmentos similares a consultas
- Recuperar documentos relevantes
- Rankear y filtrar resultados
"""

import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorRetriever:
    """
    Capa de abstraccion sobre EmbeddingGenerator para busqueda semantica.

    Atributos:
        baseVectorial : instancia de EmbeddingGenerator (contiene ChromaDB)
    """

    def __init__(self, embedding_generator=None):
        self.base_vectorial        = embedding_generator
        self.fragmentos_relevantes: List[Dict] = []
        logger.info("VectorRetriever inicializado")

    def buscar_similares(self, consulta: str, top_k: int = 5) -> List[Dict]:
        """
        Busca fragmentos similares a la consulta en ChromaDB.

        Returns:
            Lista de dicts con claves: texto, score, metadata
        """
        try:
            if self.base_vectorial is None:
                logger.error("EmbeddingGenerator no disponible")
                return []

            logger.info(f"Buscando top-{top_k} para: '{consulta[:60]}'")
            resultados = self.base_vectorial.buscar_similares(consulta, top_k)
            self.fragmentos_relevantes = resultados
            logger.info(f"{len(resultados)} fragmentos recuperados")
            return resultados
        except Exception as e:
            logger.error(f"Error en busqueda: {e}")
            return []

    def obtener_fragmentos_relevantes(self) -> List[str]:
        """Retorna solo los textos de la ultima busqueda."""
        return [f["texto"] for f in self.fragmentos_relevantes]

    def buscar_por_palabras_clave(self, palabras: List[str], top_k: int = 5) -> List[Dict]:
        """Combina busquedas individuales por palabra clave."""
        acumulado: Dict[str, Dict] = {}
        for palabra in palabras:
            for r in self.buscar_similares(palabra, top_k):
                txt = r["texto"]
                if txt not in acumulado or r["score"] > acumulado[txt]["score"]:
                    acumulado[txt] = r
        ordenados = sorted(acumulado.values(), key=lambda x: x["score"], reverse=True)
        return ordenados[:top_k]

    def obtener_top_k(self, k: int = 3) -> List[Dict]:
        """Los K mejores de la ultima busqueda."""
        return self.fragmentos_relevantes[:k]

    def rankear_por_relevancia(self, fragmentos: List[Dict]) -> List[Dict]:
        """Ordena fragmentos por score descendente."""
        return sorted(fragmentos, key=lambda x: x.get("score", 0), reverse=True)