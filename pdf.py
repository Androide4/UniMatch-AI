import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# Crear carpeta data si no existe
os.makedirs("data", exist_ok=True)


def crear_pdf_universidad(nombre_archivo, nombre_universidad, contenido_pensum):
    """Crear PDF de demostración."""

    ruta = f"data/{nombre_archivo}"

    c = canvas.Canvas(ruta, pagesize=letter)
    width, height = letter

    # Encabezado
    c.setFont("Helvetica-Bold", 18)
    c.drawString(0.7 * inch, height - 0.7 * inch, "PENSUM ACADÉMICO")

    c.setFont("Helvetica-Bold", 13)
    c.drawString(
        0.7 * inch,
        height - 1.0 * inch,
        f"Universidad: {nombre_universidad}"
    )

    # Contenido
    c.setFont("Helvetica", 10)

    y = height - 1.5 * inch

    for linea in contenido_pensum.split("\n"):
        if linea.strip():
            c.drawString(0.7 * inch, y, linea.strip())
            y -= 0.22 * inch

            if y < 1 * inch:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 1 * inch

    c.save()

    print(f"✅ PDF creado: {ruta}")


# ==========================================================
# INGENIERÍA DE SISTEMAS
# ==========================================================

contenido_sistemas_a = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD A

ENFOQUE:
Desarrollo de software y tecnologías modernas.

SEMESTRE 1:
- Programación Básica
- Matemáticas Discretas
- Álgebra Lineal
- Fundamentos de Computación

SEMESTRE 2:
- Estructuras de Datos
- Programación Orientada a Objetos
- Bases de Datos
- Desarrollo Backend

SEMESTRE 3:
- Ingeniería de Software
- Desarrollo Web
- APIs y Microservicios
- Arquitectura de Software

SEMESTRE 4:
- Inteligencia Artificial
- Cloud Computing
- Seguridad Informática
- Proyecto Final
"""

contenido_sistemas_b = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD B

ENFOQUE:
Matemáticas avanzadas e investigación computacional.

SEMESTRE 1:
- Cálculo I
- Física Computacional
- Álgebra Lineal
- Introducción a la Ingeniería

SEMESTRE 2:
- Programación Avanzada
- Matemática Discreta
- Geometría Analítica
- Laboratorio de Algoritmos

SEMESTRE 3:
- Lenguajes Formales
- Compiladores
- Teoría de la Computación
- Análisis Numérico

SEMESTRE 4:
- Investigación Operativa
- Matemática Aplicada
- Procesamiento de Señales
- Seminario de Investigación
"""

contenido_sistemas_c = """
INGENIERÍA DE SISTEMAS - UNIVERSIDAD C

ENFOQUE:
Transformación digital y emprendimiento tecnológico.

SEMESTRE 1:
- Fundamentos de Programación
- Matemáticas I
- Comunicación Académica
- Introducción a Sistemas

SEMESTRE 2:
- Programación Intermedia
- Arquitectura del Computador
- Ética Profesional
- Taller de Sistemas

SEMESTRE 3:
- Bases de Datos
- Redes Básicas
- Diseño UX/UI
- Ingeniería de Software

SEMESTRE 4:
- Seguridad de Datos
- Emprendimiento Digital
- Innovación Tecnológica
- Proyecto Integrador
"""

# ==========================================================
# INGENIERÍA ELECTRÓNICA
# ==========================================================

contenido_electronica_a = """
INGENIERÍA ELECTRÓNICA - UNIVERSIDAD A

ENFOQUE:
Automatización y sistemas embebidos.

SEMESTRE 1:
- Circuitos Básicos
- Física Eléctrica
- Álgebra Lineal
- Introducción a Electrónica

SEMESTRE 2:
- Electrónica Analógica
- Microcontroladores
- Programación Embebida
- Señales y Sistemas

SEMESTRE 3:
- Sistemas Digitales
- Automatización Industrial
- Telecomunicaciones
- Diseño Electrónico

SEMESTRE 4:
- Robótica
- Internet de las Cosas
- Sistemas Embebidos Avanzados
- Proyecto Electrónico
"""

contenido_electronica_b = """
INGENIERÍA ELECTRÓNICA - UNIVERSIDAD B

ENFOQUE:
Investigación y procesamiento de señales.

SEMESTRE 1:
- Física Moderna
- Matemáticas Aplicadas
- Circuitos I
- Introducción a Ingeniería

SEMESTRE 2:
- Electrónica Digital
- Procesamiento de Señales
- Cálculo Avanzado
- Instrumentación

SEMESTRE 3:
- Control Automático
- Electrónica Industrial
- Sistemas de Potencia
- Telecomunicaciones

SEMESTRE 4:
- Inteligencia Artificial Aplicada
- Redes Electrónicas
- Investigación Científica
- Seminario de Electrónica
"""

# ==========================================================
# FINANZAS
# ==========================================================

contenido_finanzas = """
FINANZAS - UNIVERSIDAD D

ENFOQUE:
Mercados financieros y gestión empresarial.

SEMESTRE 1:
- Introducción a Finanzas
- Matemáticas Financieras
- Economía General
- Contabilidad Básica

SEMESTRE 2:
- Gestión Financiera
- Estadística
- Microeconomía
- Análisis Financiero

SEMESTRE 3:
- Mercados de Capitales
- Riesgo Financiero
- Inversiones
- Finanzas Corporativas

SEMESTRE 4:
- Planeación Financiera
- Bolsa de Valores
- Evaluación de Proyectos
- Proyecto Empresarial
"""

# ==========================================================
# ECONOMÍA
# ==========================================================

contenido_economia = """
ECONOMÍA - UNIVERSIDAD E

ENFOQUE:
Macroeconomía y análisis económico.

SEMESTRE 1:
- Introducción a Economía
- Matemáticas I
- Historia Económica
- Fundamentos Sociales

SEMESTRE 2:
- Microeconomía
- Estadística Económica
- Economía Colombiana
- Política Pública

SEMESTRE 3:
- Macroeconomía
- Econometría
- Comercio Internacional
- Desarrollo Económico

SEMESTRE 4:
- Política Monetaria
- Finanzas Públicas
- Investigación Económica
- Seminario de Economía
"""

# ==========================================================
# CREACIÓN DE PDFs
# ==========================================================

crear_pdf_universidad(
    "universidad_a_ingenieria_sistemas.pdf",
    "Universidad A",
    contenido_sistemas_a
)

crear_pdf_universidad(
    "universidad_b_ingenieria_sistemas.pdf",
    "Universidad B",
    contenido_sistemas_b
)

crear_pdf_universidad(
    "universidad_c_ingenieria_sistemas.pdf",
    "Universidad C",
    contenido_sistemas_c
)

crear_pdf_universidad(
    "universidad_a_ingenieria_electronica.pdf",
    "Universidad A",
    contenido_electronica_a
)

crear_pdf_universidad(
    "universidad_b_ingenieria_electronica.pdf",
    "Universidad B",
    contenido_electronica_b
)

crear_pdf_universidad(
    "universidad_d_finanzas.pdf",
    "Universidad D",
    contenido_finanzas
)

crear_pdf_universidad(
    "universidad_e_economia.pdf",
    "Universidad E",
    contenido_economia
)

print("\n✅ Todos los PDFs fueron creados correctamente.")