"""
EmbeddingGenerator: Módulo responsable de generar embeddings y almacenarlos.

Responsabilidades:
- Generar embeddings usando Sentence Transformers
- Almacenar embeddings en ChromaDB
- Gestionar la base vectorial
"""

"""
EmbeddingGenerator: Genera embeddings y los almacena en ChromaDB persistente.
Lee configuracion desde .env (que ya fue cargado por main.py antes de este import).
"""

import os
import logging
import hashlib
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

# Configuracion — os.environ ya tiene los valores del .env porque main.py
# llama load_dotenv() ANTES de importar este modulo.
EMBEDDING_MODEL   = os.environ.get("EMBEDDING_MODEL",       "sentence-transformers/all-MiniLM-L6-v2")
VECTORSTORE_FOLDER= os.environ.get("VECTORSTORE_FOLDER",    "./vectorstore")
CHROMA_COLLECTION = os.environ.get("CHROMA_COLLECTION_NAME","unimatch_universidades")

try:
    from sentence_transformers import SentenceTransformer
    ST_OK = True
except ImportError:
    ST_OK = False
    logger.warning("sentence-transformers no disponible — embeddings simulados.")

try:
    import chromadb
    CHROMA_OK = True
except ImportError:
    CHROMA_OK = False
    logger.warning("chromadb no disponible — almacenamiento en memoria.")


class EmbeddingGenerator:
    """Genera embeddings y gestiona ChromaDB persistente."""

    def __init__(self):
        self.modelo_nombre = EMBEDDING_MODEL
        self.modelo        = None
        self.chroma_client = None
        self.coleccion     = None
        self._mem_store: List[Dict] = []

        self._init_modelo()
        self._init_chroma()
        logger.info("EmbeddingGenerator listo")

    # ── Init ──────────────────────────────────────────────────────────────────
    def _init_modelo(self):
        if ST_OK:
            try:
                logger.info(f"Cargando modelo de embeddings: {self.modelo_nombre}")
                self.modelo = SentenceTransformer(self.modelo_nombre)
                logger.info("Modelo listo")
            except Exception as e:
                logger.error(f"Error cargando modelo: {e}")
        else:
            logger.warning("Usando embeddings simulados")

    def _init_chroma(self):
        if not CHROMA_OK:
            logger.warning("ChromaDB no disponible — modo memoria")
            return
        try:
            Path(VECTORSTORE_FOLDER).mkdir(parents=True, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=VECTORSTORE_FOLDER)
            self.coleccion = self.chroma_client.get_or_create_collection(
                name=CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(
                f"ChromaDB OK — coleccion '{CHROMA_COLLECTION}' "
                f"con {self.coleccion.count()} docs"
            )
        except Exception as e:
            logger.error(f"Error iniciando ChromaDB: {e}")
            self.chroma_client = None
            self.coleccion     = None

    # ── Embeddings ────────────────────────────────────────────────────────────
    def generar_embeddings(self, textos: List[str]) -> List[List[float]]:
        try:
            if self.modelo:
                vecs = self.modelo.encode(textos, show_progress_bar=False)
                return vecs.tolist()
            else:
                import random
                result = []
                for t in textos:
                    seed = int(hashlib.md5(t.encode()).hexdigest(), 16) % (2**31)
                    rng  = random.Random(seed)
                    result.append([rng.gauss(0, 1) for _ in range(384)])
                return result
        except Exception as e:
            logger.error(f"Error generando embeddings: {e}")
            return []

    # ── Almacenar ─────────────────────────────────────────────────────────────
    def almacenar_en_vectorstore(
        self,
        fragmentos: List[str],
        metadata:   Dict = None,
        prefijo_id: str  = "doc",
    ) -> bool:
        """
        Guarda fragmentos en ChromaDB.
        ID unico = SHA256(prefijo + posicion + texto[:40])
        Evita duplicados usando upsert.
        """
        try:
            if not fragmentos:
                return False

            embeddings = self.generar_embeddings(fragmentos)
            if not embeddings:
                return False

            meta_lista = []
            for i in range(len(fragmentos)):
                m = (metadata or {}).copy()
                m["chunk_index"] = str(i)
                meta_lista.append(m)

            # IDs deterministas: mismo PDF + mismo chunk -> mismo ID (no duplica)
            ids = []
            for i, txt in enumerate(fragmentos):
                clave = f"{prefijo_id}_chunk{i}_{txt[:40]}"
                uid   = hashlib.sha256(clave.encode()).hexdigest()[:32]
                ids.append(uid)

            if self.coleccion is not None:
                self.coleccion.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    documents=fragmentos,
                    metadatas=meta_lista,
                )
                logger.info(f"{len(fragmentos)} fragmentos guardados en ChromaDB")
            else:
                # Fallback memoria
                for txt, emb, m in zip(fragmentos, embeddings, meta_lista):
                    self._mem_store.append({"texto": txt, "embedding": emb, "metadata": m})
                logger.info(f"{len(fragmentos)} fragmentos en memoria")
            return True

        except Exception as e:
            logger.error(f"Error almacenando: {e}")
            return False

    # ── Buscar ────────────────────────────────────────────────────────────────
    def buscar_similares(self, consulta: str, top_k: int = 5) -> List[Dict]:
        try:
            emb = self.generar_embeddings([consulta])
            if not emb:
                return []

            if self.coleccion is not None and self.coleccion.count() > 0:
                n   = min(top_k, self.coleccion.count())
                res = self.coleccion.query(query_embeddings=emb, n_results=n)
                resultados = []
                if res["documents"] and res["documents"][0]:
                    for doc, dist, meta in zip(
                        res["documents"][0],
                        res["distances"][0],
                        res["metadatas"][0],
                    ):
                        resultados.append({
                            "texto":    doc,
                            "score":    round(1 - dist, 4),
                            "metadata": meta,
                        })
                return resultados
            else:
                return self._buscar_memoria(emb[0], top_k)

        except Exception as e:
            logger.error(f"Error buscando: {e}")
            return []

    def _buscar_memoria(self, emb_q: List[float], top_k: int) -> List[Dict]:
        resultados = []
        for item in self._mem_store:
            e   = item["embedding"]
            dot = sum(a * b for a, b in zip(emb_q, e))
            nq  = sum(a**2 for a in emb_q) ** 0.5
            ne  = sum(b**2 for b in e)     ** 0.5
            sim = dot / (nq * ne) if nq > 0 and ne > 0 else 0
            resultados.append({
                "texto":    item["texto"],
                "score":    round(max(0.0, sim), 4),
                "metadata": item["metadata"],
            })
        resultados.sort(key=lambda x: x["score"], reverse=True)
        return resultados[:top_k]

    # ── Stats ─────────────────────────────────────────────────────────────────
    def obtener_estadisticas(self) -> Dict:
        total = self.coleccion.count() if self.coleccion is not None else len(self._mem_store)
        return {
            "total_documentos":   total,
            "modelo":             self.modelo_nombre,
            "vectorstore":        "ChromaDB" if self.coleccion is not None else "Memoria",
            "ruta_persistencia":  VECTORSTORE_FOLDER if self.coleccion is not None else "N/A",
        }