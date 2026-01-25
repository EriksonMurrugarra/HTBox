from selenium.common.exceptions import TimeoutException
from spotify_page import SpotifyPage
from logger_config import logger
from exceptions import AppNotFoundException


class SpotifyFlow1:
    """
    Flujo 1 de automatización de Spotify.
    Busca un artista, selecciona el elemento verificado y reproduce música.
    """
    
    def __init__(self, driver, artist_name: str = "Martin Garrix"):
        """
        Inicializa el flujo con el driver y el nombre del artista.
        
        Args:
            driver: Instancia de WebDriver (Appium)
            artist_name: Nombre del artista a buscar (default: "Martin Garrix")
        """
        self.driver = driver
        self.spotify = SpotifyPage(driver)
        self.artist_name = artist_name
    
    def execute(self):
        """
        Ejecuta el flujo completo de automatización.
        
        Returns:
            None
        
        Raises:
            TimeoutException: Si ocurre un timeout durante la ejecución
            AppNotFoundException: Si la aplicación no se encuentra o no puede ser abierta
        """
        logger.info(f"[spotify_flow_1] [execute] Iniciando sleep_random...")
        self.spotify.sleep_random(2, 5)
        logger.info(f"[spotify_flow_1] [execute] sleep_random completado")
       
        try:
            logger.info(f"[spotify_flow_1] [execute] Abriendo la aplicación...")
            self.spotify.open_app(app_name = "com.spotify.music")
            logger.info(f"[spotify_flow_1] [execute] open_app completado exitosamente")
        except AppNotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"[spotify_flow_1] [execute] Error inesperado al abrir la app: {e}", exc_info=True)
            raise
        
        self.spotify.sleep_random(2, 5)

        self.spotify.check_banners()
        
        
        try:
            # click search tab
            search_tab = self.spotify.get_search_tab()        
            self.spotify.sleep_random(2, 5)            
            search_tab.click()
            
            
            # search artist
            self.spotify.sleep_random(2, 5)
            self.spotify.change_search_text(self.artist_name)
            
            # get verified element
            verified_element = self.spotify.get_verified_element()
            verified_element.click()
            
            self.spotify.sleep_random(3, 5)    
            play_pause_button = self.spotify.get_artist_play_button()

            play_pause_button.click()

        except TimeoutException:
            logger.error(f"[spotify_flow_1] [execute] Error: La aplicación no cargó completamente después de 30 segundos. ❌")
            logger.warning(f"[spotify_flow_1] [execute] Intentando verificar el estado de la app...")
            
            # Intentar obtener información del estado actual
            try:
                current_package = self.driver.current_package
                logger.info(f"[spotify_flow_1] [execute] Paquete actual: {current_package}")
                if current_package != "com.spotify.music":
                    logger.warning(f"[spotify_flow_1] [execute] La app no está en primer plano. Intentando abrirla de nuevo...")
                    try:
                        self.spotify.open_app("com.spotify.music")
                        self.spotify.sleep_random(5, 10)
                    except AppNotFoundException as e:
                        logger.error(f"[spotify_flow_1] [execute] Error crítico al intentar reabrir la app: {e}")
                        logger.error(f"[spotify_flow_1] [execute] Terminando ejecución del flujo. ❌")
                        return  # Terminar la ejecución del flujo
            except Exception as e:
                logger.error(f"[spotify_flow_1] [execute] Error al verificar estado: {e}", exc_info=True)
            
            raise
