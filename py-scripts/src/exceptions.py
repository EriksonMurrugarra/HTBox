"""
Excepciones personalizadas para la automatización de Spotify.
"""


class AppNotFoundException(Exception):
    """
    Excepción lanzada cuando una aplicación no se encuentra o no puede ser abierta.
    """
    
    def __init__(self, app_name: str, message: str = None):
        """
        Inicializa la excepción.
        
        Args:
            app_name: Nombre del paquete de la aplicación que no se encontró
            message: Mensaje personalizado (opcional)
        """
        self.app_name = app_name
        if message is None:
            message = f"La aplicación '{app_name}' no se encontró o no puede ser abierta."
        super().__init__(f"[APP_NOT_FOUND]: {message}")
