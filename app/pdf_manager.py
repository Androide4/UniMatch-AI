"""
PdfManager: Módulo responsable de gestionar y cargar PDFs desde una carpeta local.

Responsabilidades:
- Leer automáticamente una carpeta interna con PDFs
- Validar archivos PDF
- Proporcionar lista de documentos disponibles
- Rastrear rutas de PDFs para posterior procesamiento
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDF:
    """Clase que representa un documento PDF."""
    
    def __init__(self, nombre: str, ruta: str):
        """
        Inicializar un objeto PDF.
        
        Args:
            nombre (str): Nombre del archivo PDF
            ruta (str): Ruta completa al archivo PDF
        """
        self.nombre = nombre
        self.ruta = ruta
        self.tamaño = os.path.getsize(ruta) if os.path.exists(ruta) else 0
        
    def __repr__(self):
        return f"PDF(nombre='{self.nombre}', tamaño={self.tamaño} bytes)"


class PdfManager:
    """
    Gestor de PDFs que lee automáticamente una carpeta interna.
    
    Atributos:
        ruta_carpeta (str): Ruta a la carpeta que contiene los PDFs
        lista_pdfs (List[PDF]): Lista de objetos PDF cargados
    """
    
    def __init__(self, ruta_carpeta: str = "./data"):
        """
        Inicializar el gestor de PDFs.
        
        Args:
            ruta_carpeta (str): Ruta a la carpeta con PDFs (default: ./data)
        """
        self.ruta_carpeta = Path(ruta_carpeta)
        self.lista_pdfs: List[PDF] = []
        
        # Validar que la carpeta exista
        if not self.ruta_carpeta.exists():
            logger.warning(f"⚠️  La carpeta '{self.ruta_carpeta}' no existe.")
            logger.info(f"📁 Creando carpeta: {self.ruta_carpeta}")
            self.ruta_carpeta.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ PdfManager inicializado con carpeta: {self.ruta_carpeta}")
    
    def cargar_pdfs(self) -> List[PDF]:
        """
        Cargar automáticamente todos los PDFs de la carpeta.
        
        Returns:
            List[PDF]: Lista de objetos PDF encontrados
        """
        logger.info("🔍 Buscando PDFs en la carpeta...")
        
        # Limpiar lista anterior
        self.lista_pdfs = []
        
        # Buscar archivos .pdf en la carpeta
        archivos_pdf = list(self.ruta_carpeta.glob("*.pdf"))
        
        if not archivos_pdf:
            logger.warning(f"⚠️  No se encontraron PDFs en {self.ruta_carpeta}")
            return []
        
        # Procesar cada archivo PDF encontrado
        for archivo in archivos_pdf:
            try:
                # Validar que sea un archivo PDF válido
                if self._validar_pdf(archivo):
                    pdf = PDF(archivo.name, str(archivo))
                    self.lista_pdfs.append(pdf)
                    logger.info(f"✅ PDF cargado: {archivo.name} ({pdf.tamaño} bytes)")
                else:
                    logger.warning(f"⚠️  Archivo inválido o no es PDF: {archivo.name}")
            except Exception as e:
                logger.error(f"❌ Error procesando {archivo.name}: {e}")
        
        logger.info(f"📊 Total de PDFs cargados: {len(self.lista_pdfs)}")
        return self.lista_pdfs
    
    def _validar_pdf(self, ruta_archivo: Path) -> bool:
        """
        Validar que un archivo sea un PDF válido.
        
        Args:
            ruta_archivo (Path): Ruta al archivo a validar
            
        Returns:
            bool: True si es un PDF válido, False en caso contrario
        """
        try:
            # Validar extensión
            if not ruta_archivo.suffix.lower() == ".pdf":
                return False
            
            # Validar que sea un archivo existente
            if not ruta_archivo.is_file():
                return False
            
            # Validar que tenga contenido (al menos 100 bytes para desarrollo)
            if ruta_archivo.stat().st_size < 100:
                logger.warning(f"⚠️  {ruta_archivo.name} es muy pequeño (< 100B)")
                return False
            
            # Validar header PDF (comienza con %PDF)
            with open(ruta_archivo, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    logger.warning(f"⚠️  {ruta_archivo.name} no tiene header PDF válido")
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validando PDF: {e}")
            return False
    
    def obtener_documentos(self) -> List[PDF]:
        """
        Obtener lista de documentos PDF cargados.
        
        Returns:
            List[PDF]: Lista de objetos PDF disponibles
        """
        if not self.lista_pdfs:
            logger.info("ℹ️  Lista de PDFs vacía. Ejecutando cargar_pdfs()...")
            self.cargar_pdfs()
        
        return self.lista_pdfs
    
    def obtener_rutas_pdfs(self) -> List[str]:
        """
        Obtener solo las rutas de los PDFs como strings.
        
        Returns:
            List[str]: Lista de rutas completas a los PDFs
        """
        return [pdf.ruta for pdf in self.obtener_documentos()]
    
    def obtener_nombres_pdfs(self) -> List[str]:
        """
        Obtener solo los nombres de los PDFs.
        
        Returns:
            List[str]: Lista de nombres de PDFs
        """
        return [pdf.nombre for pdf in self.obtener_documentos()]
    
    def obtener_info_pdfs(self) -> Dict[str, Dict]:
        """
        Obtener información detallada de todos los PDFs.
        
        Returns:
            Dict: Diccionario con información de cada PDF
        """
        info = {}
        for pdf in self.obtener_documentos():
            info[pdf.nombre] = {
                "ruta": pdf.ruta,
                "tamaño_bytes": pdf.tamaño,
                "tamaño_mb": round(pdf.tamaño / (1024 * 1024), 2)
            }
        return info
    
    def obtener_pdf_por_nombre(self, nombre: str) -> Optional[PDF]:
        """
        Obtener un PDF específico por nombre.
        
        Args:
            nombre (str): Nombre del PDF (ej: "universidad_a.pdf")
            
        Returns:
            Optional[PDF]: Objeto PDF si existe, None en caso contrario
        """
        for pdf in self.obtener_documentos():
            if pdf.nombre.lower() == nombre.lower():
                return pdf
        return None
    
    def contar_pdfs(self) -> int:
        """
        Contar total de PDFs disponibles.
        
        Returns:
            int: Cantidad de PDFs cargados
        """
        return len(self.obtener_documentos())


# ============================================================================
# EJEMPLO DE USO Y PRUEBAS
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 PRUEBA: PdfManager")
    print("="*70 + "\n")
    
    # Crear instancia del gestor
    manager = PdfManager(ruta_carpeta="./data")
    
    # Cargar PDFs
    print("\n📌 Paso 1: Cargar PDFs desde la carpeta")
    print("-" * 70)
    pdfs = manager.cargar_pdfs()
    print(f"PDFs encontrados: {len(pdfs)}")
    for pdf in pdfs:
        print(f"  - {pdf}")
    
    # Obtener documentos
    print("\n📌 Paso 2: Obtener documentos cargados")
    print("-" * 70)
    docs = manager.obtener_documentos()
    print(f"Total documentos: {len(docs)}")
    
    # Obtener rutas
    print("\n📌 Paso 3: Obtener rutas de PDFs")
    print("-" * 70)
    rutas = manager.obtener_rutas_pdfs()
    for ruta in rutas:
        print(f"  - {ruta}")
    
    # Obtener nombres
    print("\n📌 Paso 4: Obtener nombres de PDFs")
    print("-" * 70)
    nombres = manager.obtener_nombres_pdfs()
    for nombre in nombres:
        print(f"  - {nombre}")
    
    # Obtener información detallada
    print("\n📌 Paso 5: Información detallada de PDFs")
    print("-" * 70)
    info = manager.obtener_info_pdfs()
    for nombre, datos in info.items():
        print(f"  📄 {nombre}")
        print(f"     Ruta: {datos['ruta']}")
        print(f"     Tamaño: {datos['tamaño_mb']} MB")
    
    # Buscar PDF específico
    print("\n📌 Paso 6: Buscar PDF específico")
    print("-" * 70)
    if pdfs:
        nombre_buscar = pdfs[0].nombre
        resultado = manager.obtener_pdf_por_nombre(nombre_buscar)
        print(f"Buscando: {nombre_buscar}")
        print(f"Encontrado: {resultado}")
    
    # Contar PDFs
    print("\n📌 Paso 7: Contar PDFs")
    print("-" * 70)
    total = manager.contar_pdfs()
    print(f"Total de PDFs en el sistema: {total}")
    
    print("\n" + "="*70)
    print("✅ PRUEBA COMPLETADA")
    print("="*70 + "\n")