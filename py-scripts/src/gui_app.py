"""
Punto de entrada para la aplicación con interfaz gráfica.
Ejecuta la GUI en lugar de la versión de línea de comandos.
"""
import sys
import os

# Agregar el directorio src al path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from gui.main_window import MainWindow
from logger_config import logger
import customtkinter as ctk


def main():
    """
    Función principal que inicia la aplicación GUI.
    """
    try:
        logger.info("=" * 60)
        logger.info("Iniciando HTBox - Spotify Automation GUI")
        logger.info("=" * 60)
        
        # Crear y ejecutar la ventana principal
        app = MainWindow()
        
        # Configurar el handler de cierre
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Iniciar el loop principal
        app.mainloop()
        
        logger.info("Aplicación cerrada correctamente")
        
    except KeyboardInterrupt:
        logger.info("Aplicación interrumpida por el usuario")
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

