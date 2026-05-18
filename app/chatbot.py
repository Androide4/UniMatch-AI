"""
Chatbot: Módulo de interfaz conversacional para usuarios.

Responsabilidades:
- Recibir mensajes de usuarios
- Procesar consultas mediante QueryEngine
- Mantener historial de sesión
- Enviar respuestas formateadas
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SesionChat:
    """Representa una sesion de conversacion."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.inicio     = datetime.now()
        self.mensajes: List[Dict] = []

    def agregar(self, rol: str, contenido: str):
        self.mensajes.append({
            "rol":       rol,
            "contenido": contenido,
            "timestamp": datetime.now().isoformat(),
        })

    def historial(self) -> List[Dict]:
        return self.mensajes

    def duracion(self) -> str:
        return str(datetime.now() - self.inicio).split(".")[0]


class Chatbot:
    """
    Chatbot de UniMatch AI.

    Atributos:
        queryEngine : instancia de QueryEngine
        sessionId   : ID de sesion actual
        memory      : historial de mensajes (delegado a SesionChat)
    """

    BIENVENIDA = (
        "Hola! Soy UniMatch AI, tu asistente de orientacion universitaria.\n"
        "Puedo ayudarte a comparar programas academicos y recomendarte la mejor opcion "
        "segun los pensum disponibles.\n\n"
        "Ejemplos de preguntas:\n"
        "  - Quiero estudiar Ingenieria de Sistemas, que universidad me recomiendas?\n"
        "  - Cual universidad tiene mas enfoque en programacion?\n"
        "  - Que materias tiene la Universidad A en primer semestre?"
    )

    def __init__(self, query_engine=None, session_id: str = None):
        self.query_engine  = query_engine
        self.session_id    = session_id or f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.sesion_actual = SesionChat(self.session_id)
        logger.info(f"Chatbot listo – sesion: {self.session_id}")

    # ── API principal ─────────────────────────────────────────────────────────
    def recibir_mensaje(self, mensaje: str) -> Dict:
        """
        Procesa un mensaje del usuario y devuelve la respuesta.

        Returns:
            {"respuesta": str, "session_id": str, "exito": bool}
        """
        try:
            mensaje = mensaje.strip()
            if not mensaje:
                return self._respuesta("Por favor escribe tu pregunta.", exito=False)

            logger.info(f"Mensaje recibido: '{mensaje[:60]}'")
            self.sesion_actual.agregar("user", mensaje)

            # Comandos especiales
            if mensaje.lower() in ("ayuda", "help", "/ayuda"):
                respuesta = self.BIENVENIDA
            elif mensaje.lower() in ("nuevo", "reiniciar", "/nuevo"):
                self.reiniciar_sesion()
                respuesta = "Sesion reiniciada. Como puedo ayudarte?"
            else:
                respuesta = self._procesar_con_engine(mensaje)

            self.sesion_actual.agregar("assistant", respuesta)
            logger.info("Respuesta enviada")
            return self._respuesta(respuesta)

        except Exception as e:
            logger.error(f"Error en chatbot: {e}")
            return self._respuesta("Ocurrio un error. Intenta de nuevo.", exito=False)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _procesar_con_engine(self, mensaje: str) -> str:
        if self.query_engine:
            resultado = self.query_engine.procesar_consulta(mensaje)
            return resultado.get("respuesta", "No pude generar una respuesta.")
        return self._respuesta_sin_engine(mensaje)

    def _respuesta_sin_engine(self, mensaje: str) -> str:
        """Respuestas basicas cuando QueryEngine no esta disponible."""
        m = mensaje.lower()
        if any(w in m for w in ("hola", "hi", "buenos")):
            return self.BIENVENIDA
        if any(w in m for w in ("ingenieria", "sistemas", "programa")):
            return "Tengo informacion sobre programas de Ingenieria de Sistemas. Puedes preguntar por una universidad especifica."
        if any(w in m for w in ("comparar", "diferencia", "mejor")):
            return "Para comparar universidades necesito que el sistema este completamente inicializado. Ejecuta: python main.py"
        return "Pregunta sobre carreras universitarias y te ayudare a encontrar la mejor opcion."

    def _respuesta(self, texto: str, exito: bool = True) -> Dict:
        return {
            "respuesta":  texto,
            "session_id": self.session_id,
            "timestamp":  datetime.now().isoformat(),
            "exito":      exito,
        }

    def reiniciar_sesion(self):
        self.session_id    = f"chat_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.sesion_actual = SesionChat(self.session_id)
        if self.query_engine:
            self.query_engine.limpiar_memoria()
        logger.info(f"Sesion reiniciada: {self.session_id}")

    def obtener_historial_sesion(self) -> List[Dict]:
        return self.sesion_actual.historial()

    def obtener_contexto_sesion(self) -> Dict:
        h = self.sesion_actual.historial()
        return {
            "session_id":    self.session_id,
            "total_mensajes": len(h),
            "turnos_usuario": sum(1 for m in h if m["rol"] == "user"),
            "duracion":       self.sesion_actual.duracion(),
        }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PRUEBA: Chatbot")
    print("=" * 70)

    bot = Chatbot()

    conversacion = [
        "Hola!",
        "Quiero estudiar Ingenieria de Sistemas",
        "Cual universidad recomiendas?",
        "Gracias",
    ]

    for msg in conversacion:
        print(f"\nUsuario: {msg}")
        r = bot.recibir_mensaje(msg)
        print(f"Bot: {r['respuesta'][:200]}")

    print(f"\nContexto: {bot.obtener_contexto_sesion()}")
    print("\n" + "=" * 70)
    print("PRUEBA COMPLETADA")
    print("=" * 70 + "\n")