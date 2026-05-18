import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Crear carpeta data si no existe
os.makedirs("data", exist_ok=True)

# Función para crear un PDF de demostración
def crear_pdf_universidad(nombre_archivo, nombre_universidad, contenido_pensum):
    """Crear un PDF de demostración con contenido de pensum."""
    ruta = f"data/{nombre_archivo}"
    
    c = canvas.Canvas(ruta, pagesize=letter)
    width, height = letter
    
    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.5*inch, height - 0.5*inch, f"PENSUM ACADÉMICO")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.5*inch, height - 0.8*inch, f"Universidad: {nombre_universidad}")
    
    # Contenido
    c.setFont("Helvetica", 10)
    y_pos = height - 1.2*inch
    
    for linea in contenido_pensum.split('\n'):
        if linea.strip():
            c.drawString(0.5*inch, y_pos, linea)
            y_pos -= 0.2*inch
    
    c.save()
    print(f"✅ PDF creado: {ruta}")

# Crear PDFs de demostración
contenido_1 = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD A

SEMESTRE 1:
- Programación Básica (Python)
- Matemáticas Discretas
- Álgebra Lineal
- Fundamentos de Computación
- Lógica Digital

SEMESTRE 2:
- Estructuras de Datos
- Programación Orientada a Objetos
- Cálculo Diferencial
- Análisis de Algoritmos
- Bases de Datos Relacionales

SEMESTRE 3:
- Desarrollo de Software
- Ingeniería de Software
- Sistemas Operativos
- Redes de Computadores
- Arquitectura de Sistemas

SEMESTRE 4:
- Bases de Datos Avanzadas
- Seguridad Informática
- Desarrollo Web
- Inteligencia Artificial
- Proyecto Final
"""

contenido_2 = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD B

SEMESTRE 1:
- Algoritmos y Programación
- Cálculo I
- Álgebra Lineal
- Física Computacional
- Introducción a la Ingeniería

SEMESTRE 2:
- Programación Avanzada
- Cálculo II
- Geometría Analítica
- Laboratorio de Programación
- Matemática Discreta

SEMESTRE 3:
- Análisis Numérico
- Teoría de Autómatas
- Lenguajes Formales
- Compiladores
- Teoría de la Computación

SEMESTRE 4:
- Investigación Operativa
- Matemática Aplicada
- Procesamiento de Señales
- Control Automático
- Seminario de Investigación
"""

contenido_3 = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD C

SEMESTRE 1:
- Fundamentos de Programación
- Matemáticas I
- Introducción a Sistemas
- Lógica Proporcional
- Comunicación Académica

SEMESTRE 2:
- Programación Intermedia
- Matemáticas II
- Arquitectura del Computador
- Taller de Sistemas
- Ética Profesional

SEMESTRE 3:
- Ingeniería de Software I
- Bases de Datos
- Redes Básicas
- Diseño de Interfaces
- Seminario Tecnológico

SEMESTRE 4:
- Ingeniería de Software II
- Seguridad de Datos
- Administración de Redes
- Emprendimiento Digital
- Proyecto Integrador
"""

# Crear los PDFs
crear_pdf_universidad("universidad_a_ingenieria_sistemas.pdf", "Universidad A", contenido_1)
crear_pdf_universidad("universidad_b_ingenieria_sistemas.pdf", "Universidad B", contenido_2)
crear_pdf_universidad("universidad_c_ingenieria_sistemas.pdf", "Universidad C", contenido_3)

print("\n✅ PDFs de demostración creados exitosamente")