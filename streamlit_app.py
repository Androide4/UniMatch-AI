"""
streamlit_app.py - Interfaz grafica de UniMatch AI.
Ejecutar con: streamlit run streamlit_app.py
"""

# ── Cargar .env ANTES que cualquier otra cosa ─────
import os
from dotenv import load_dotenv
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)

import streamlit as st

st.set_page_config(
    page_title="UniMatch AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.user-msg { background:#dbeafe; border-left:4px solid #2563eb;
            padding:.75rem 1rem; border-radius:8px; margin:.4rem 0; }
.bot-msg  { background:#f0fdf4; border-left:4px solid #16a34a;
            padding:.75rem 1rem; border-radius:8px; margin:.4rem 0; }
.ok   { color:#16a34a; font-weight:bold; }
.warn { color:#dc2626; font-weight:bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Iniciando UniMatch AI…")
def cargar_sistema():
    from main import UnimatchAI
    # limpiar_bd=True: borra datos de prueba previos y re-indexa limpio
    sistema = UnimatchAI(limpiar_bd=True)
    sistema.procesar_pdfs()
    return sistema


def main():
    st.title("🎓 UniMatch AI")
    st.caption("Sistema de recomendacion de universidades basado en analisis de pensum")

    # Verificar key en tiempo de render (informativo)
    groq_key_presente = bool(os.environ.get("GROQ_API_KEY", ""))

    try:
        sistema = cargar_sistema()
    except Exception as e:
        st.error(f"Error iniciando el sistema: {e}")
        st.stop()

    stats = sistema.obtener_estadisticas()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("⚙️ Panel de control")

        c1, c2 = st.columns(2)
        c1.metric("PDFs",        stats["pdfs_disponibles"])
        c2.metric("Fragmentos",  stats["embeddings"].get("total_documentos", 0))

        # Estado Groq
        if stats.get("groq_activo") and groq_key_presente:
            st.markdown('<p class="ok">✅ Groq conectado</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="warn">⚠️ Groq sin clave — revisa .env</p>',
                        unsafe_allow_html=True)
            with st.expander("¿Cómo agregar la clave Groq?"):
                st.code(
                    "# En tu archivo .env escribe:\n"
                    "GROQ_API_KEY=gsk_tu_clave_aqui",
                    language="bash",
                )
                st.info("Luego detén Streamlit (Ctrl+C) y vuelve a correrlo.")

        st.divider()

        # Re-indexar PDFs
        if st.button("🔄 Re-indexar PDFs", use_container_width=True,
                     help="Borra la BD y vuelve a leer todos los PDFs"):
            with st.spinner("Re-indexando…"):
                sistema.embedding_generator._limpiar_coleccion() if hasattr(
                    sistema.embedding_generator, "_limpiar_coleccion") else None
                sistema._limpiar_coleccion()
                sistema.procesar_pdfs(forzar_reindexado=True)
            st.cache_resource.clear()
            st.success("Re-indexado completo!")
            st.rerun()

        # Nueva conversacion
        if st.button("💬 Nueva conversacion", use_container_width=True):
            st.session_state.historial = []
            sistema.chatbot.reiniciar_sesion()
            st.rerun()

        st.divider()

        st.subheader("📄 PDFs indexados")
        pdfs = sistema.pdf_manager.obtener_documentos()
        if pdfs:
            for pdf in pdfs:
                st.write(f"• {pdf.nombre}")
        else:
            st.warning("Sin PDFs. Agrega archivos a /data/ y pulsa Re-indexar.")

        st.divider()

        st.subheader("💡 Preguntas de ejemplo")
        ejemplos = [
            "Cual universidad es mejor para programar?",
            "Que materias tiene el primer semestre?",
            "Compara todas las universidades",
            "Cual tiene mas enfoque matematico?",
        ]
        for ej in ejemplos:
            if st.button(ej, key=f"ej_{ej[:15]}", use_container_width=True):
                st.session_state.pregunta_rapida = ej
                st.rerun()

    # ── Chat ──────────────────────────────────────────────────────────────────
    st.subheader("💬 Asistente de orientacion universitaria")

    if "historial" not in st.session_state:
        st.session_state.historial = []

    if not st.session_state.historial:
        st.info(
            "Hola! Puedo comparar universidades segun sus planes de estudio. "
            "Escribe tu pregunta o usa los ejemplos del panel lateral."
        )

    for msg in st.session_state.historial:
        if msg["rol"] == "user":
            st.markdown(
                f'<div class="user-msg"><b>Tú:</b> {msg["contenido"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="bot-msg"><b>🎓 UniMatch:</b> {msg["contenido"]}</div>',
                unsafe_allow_html=True,
            )

    # Capturar pregunta rapida del sidebar
    pregunta_inicial = st.session_state.pop("pregunta_rapida", "")

    with st.form("form_chat", clear_on_submit=True):
        col_in, col_btn = st.columns([5, 1])
        with col_in:
            entrada = st.text_input(
                "Pregunta",
                value=pregunta_inicial,
                placeholder="Ej: Cual universidad tiene mas materias de programacion?",
                label_visibility="collapsed",
            )
        with col_btn:
            enviar = st.form_submit_button("Enviar ➤", use_container_width=True)

    if enviar and entrada.strip():
        st.session_state.historial.append({"rol": "user", "contenido": entrada.strip()})
        with st.spinner("Consultando pensum…"):
            respuesta = sistema.chatear(entrada.strip())
        st.session_state.historial.append({"rol": "assistant", "contenido": respuesta})
        st.rerun()

    # ── Tabs inferiores ───────────────────────────────────────────────────────
    st.divider()
    tab1, tab2 = st.tabs(["📊 Estado del sistema", "🔍 Busqueda directa"])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("PDFs",          stats["pdfs_disponibles"])
        c2.metric("Fragmentos BD", stats["embeddings"].get("total_documentos", 0))
        c3.metric("Vectorstore",   stats["embeddings"].get("vectorstore", "N/A"))
        c4.metric("Groq",          "Activo" if stats.get("groq_activo") else "Inactivo")

        st.caption(f"Ruta ChromaDB: {stats['embeddings'].get('ruta_persistencia', 'N/A')}")
        st.caption(f"Modelo embeddings: {stats['embeddings'].get('modelo', 'N/A')}")

    with tab2:
        st.subheader("Busqueda semantica directa en ChromaDB")
        consulta_dir = st.text_input("Consulta:", key="busq_dir",
                                     placeholder="Ej: programacion orientada a objetos")
        top_k = st.slider("Resultados", 1, 10, 3, key="top_k_dir")

        if st.button("🔍 Buscar", key="btn_busq"):
            if consulta_dir.strip():
                resultados = sistema.vector_retriever.buscar_similares(
                    consulta_dir.strip(), top_k=top_k
                )
                if resultados:
                    for i, r in enumerate(resultados, 1):
                        univ = r.get("metadata", {}).get("universidad", "Desconocida")
                        with st.expander(
                            f"[{i}] {univ} — Score: {r['score']:.3f}"
                        ):
                            st.write(r["texto"])
                            st.json(r.get("metadata", {}))
                else:
                    st.warning("Sin resultados. Verifica que los PDFs esten indexados.")
            else:
                st.warning("Escribe una consulta.")


if __name__ == "__main__":
    main()