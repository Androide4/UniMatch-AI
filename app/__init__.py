"""
UniMatch AI - Sistema de Recomendación de Universidades

Módulos principales:
- pdf_manager: Gestión de PDFs
- pdf_extractor: Extracción de texto
- embedding_generator: Generación de embeddings
- vector_retriever: Recuperación de información
- query_engine: Procesamiento de consultas
- chatbot: Interfaz conversacional
"""

from .pdf_manager import PdfManager, PDF
from .pdf_extractor import PdfExtractor
from .embedding_generator import EmbeddingGenerator
from .vector_retriever import VectorRetriever
from .query_engine import QueryEngine
from .chatbot import Chatbot, SesionChat

__version__ = "1.0.0"
__author__ = "UniMatch AI Development Team"

__all__ = [
    'PdfManager',
    'PDF',
    'PdfExtractor',
    'EmbeddingGenerator',
    'VectorRetriever',
    'QueryEngine',
    'Chatbot',
    'SesionChat'
]