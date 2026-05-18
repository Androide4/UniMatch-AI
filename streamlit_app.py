"""
streamlit_app.py - Interfaz grafica de UniMatch AI.
Ejecutar con: streamlit run streamlit_app.py
"""

# ── Cargar .env ANTES que cualquier otra cosa ─────
import os
from dotenv import load_dotenv
import streamlit as st

# Cargar .env
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)

st.set_page_config(
    page_title="UniMatch AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── CSS Moderno ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .sub-header {
        text-align: center;
        color: #475569;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .user-msg {
        background: #dbeafe;
        border-radius: 18px 18px 4px 18px;
        padding: 1rem 1.2rem;
        margin: 0.7rem 0;
        max-width: 85%;
        color: #1e40af;
    }
    .bot-msg {
        background: #f1f5f9;
        border-radius: 18px 18px 18px 4px;
        padding: 1rem 1.2rem;
        margin: 0.7rem 0;
        max-width: 85%;
        color: #0f172a;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Iniciando UniMatch AI...")
def cargar_sistema():
    from main import UnimatchAI
    sistema = UnimatchAI(limpiar_bd=True)
    sistema.procesar_pdfs()
    return sistema


def main():
    # Header Elegante
    st.markdown('<h1 class="main-header">🎓 UniMatch AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Tu asistente inteligente para comparar planes de estudio universitarios</p>', 
                unsafe_allow_html=True)

    try:
        sistema = cargar_sistema()
    except Exception as e:
        st.error(f"Error al iniciar el sistema: {e}")
        st.stop()

    # ── Sidebar Limpia ─────────────────────────────────────────────────────
    with st.sidebar:
        st.header("Opciones")

        if st.button("💬 Nueva Conversación", use_container_width=True):
            st.session_state.historial = []
            sistema.chatbot.reiniciar_sesion()
            st.rerun()

        st.divider()

        # Estado Groq
        groq_ok = bool(os.getenv("GROQ_API_KEY"))
        if groq_ok:
            st.success("✅ Groq conectado")
        else:
            st.warning("⚠️ Groq no configurado")

        st.divider()

        # Preguntas de ejemplo
        st.subheader("💡 Ejemplos")
        ejemplos = [
            "Quiero estudiar Ingeniería de Sistemas",
            "Compara las universidades disponibles",
            "Cuál tiene mejor enfoque en IA y Machine Learning?",
            "Qué universidad recomiendas para programación?",
            "Compara el primer semestre entre las universidades",
        ]
        for ej in ejemplos:
            if st.button(ej, key=f"ej_{ej[:25]}", use_container_width=True):
                st.session_state.pregunta_rapida = ej
                st.rerun()

    # ── Chat Principal ─────────────────────────────────────────────────────
    if "historial" not in st.session_state:
        st.session_state.historial = []

    if not st.session_state.historial:
        st.info("""
        👋 ¡Hola! Soy **UniMatch AI**.  
        Puedo ayudarte a comparar planes de estudio y recomendarte la mejor universidad según tus intereses.
        """)

    # Mostrar historial
    for msg in st.session_state.historial:
        if msg["rol"] == "user":
            st.markdown(f'<div class="user-msg"><b>Tú:</b> {msg["contenido"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-msg"><b>🎓 UniMatch AI:</b><br>{msg["contenido"]}</div>', 
                       unsafe_allow_html=True)

    # Input del chat
    pregunta_inicial = st.session_state.pop("pregunta_rapida", "")

    with st.form("chat_form", clear_on_submit=True):
        entrada = st.text_input(
            "",
            value=pregunta_inicial,
            placeholder="Escribe tu pregunta aquí... (Ej: Quiero estudiar Ingeniería de Sistemas con énfasis en IA)",
            label_visibility="collapsed"
        )
        enviar = st.form_submit_button("Enviar", use_container_width=True, type="primary")

    if enviar and entrada.strip():
        st.session_state.historial.append({"rol": "user", "contenido": entrada.strip()})
        
        with st.spinner("Analizando los planes de estudio..."):
            respuesta = sistema.chatear(entrada.strip())
        
        st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})
        st.rerun()


if __name__ == "__main__":
    main()