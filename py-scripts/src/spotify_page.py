from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from app_page import AppPage
from logger_config import logger


class SpotifyPage(AppPage):
    """
    Clase para interactuar con la aplicación Spotify usando Appium.
    Proporciona métodos reutilizables para automatizar acciones en Spotify.
    """
    
    def __init__(self, driver, wait_timeout: int = 30):
        """
        Inicializa la clase SpotifyPage.
        
        Args:
            driver: Instancia de WebDriver (Appium)
            wait_timeout: Tiempo máximo de espera en segundos (default: 30)
        """
        super().__init__(driver)
        self.wait = WebDriverWait(driver, wait_timeout)
    
    def get_search_tab(self):
        """
        Obtiene el botón/pestaña de búsqueda de Spotify.
        
        Returns:
            WebElement: Elemento del botón de búsqueda
        
        Raises:
            TimeoutException: Si no se encuentra el elemento dentro del timeout
        """
        logger.debug("Buscando el botón de búsqueda...")
        try:
            # Intentar encontrar el botón de búsqueda por XPath primero
            search_tab = self.wait.until(
                EC.presence_of_element_located((AppiumBy.XPATH, 
                    "//android.view.ViewGroup[@resource-id='com.spotify.music:id/navigation_bar']/android.view.View/android.view.View[2]/android.view.View[2]"))
            )
            logger.debug("Botón de búsqueda encontrado por XPath!")
            return search_tab
        except TimeoutException:
            # Si no se encuentra por XPath, intentar por ID
            logger.debug("No se encontró por XPath, intentando por ID...")
            search_tab = self.wait.until(
                EC.presence_of_element_located((AppiumBy.ID, "com.spotify.music:id/button_search"))
            )
            logger.debug("Botón de búsqueda encontrado por ID!")
            return search_tab
    
    def get_search_field(self):
        """
        Obtiene el campo de búsqueda de Spotify y hace click en él.
        
        Returns:
            WebElement: Elemento EditText del campo de búsqueda
        
        Raises:
            TimeoutException: Si no se encuentra el elemento dentro del timeout
        """
        logger.debug("Buscando el campo de búsqueda...")
        # Primero hacer click en el contenedor del campo de búsqueda
        search_field_container = self.wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, 
                "//androidx.compose.ui.platform.ComposeView[@resource-id='com.spotify.music:id/browse_search_bar_container']/android.view.View/android.view.View"))
        )
        logger.debug("Campo de búsqueda encontrado!")
        
        # Hacer click en el campo de búsqueda
        search_field_container.click()
        logger.debug("Click en el campo de búsqueda!")
        
        # Esperar un momento para que el teclado aparezca
        self.sleep(1)
        
        # Buscar el EditText donde debemos escribir
        logger.debug("Buscando el EditText para escribir...")
        edit_text = self.wait.until(
            EC.element_to_be_clickable((AppiumBy.XPATH, "//android.widget.EditText[@resource-id='com.spotify.music:id/query']"))
        )
        logger.debug("EditText encontrado!")
        return edit_text
    
    def change_search_text(self, text: str):
        """
        Cambia el texto en el campo de búsqueda de Spotify.
        
        Args:
            text: Texto a buscar
        
        Returns:
            None
        """
        edit_text = self.get_search_field()
        
        # Escribir el texto en el EditText
        edit_text.send_keys(text)
        logger.info(f"Texto '{text}' escrito en el campo de búsqueda!")
        
        # Esperar a que aparezcan los resultados de búsqueda
        logger.debug("Esperando a que aparezcan los resultados...")
        self.sleep(3)  # Esperar a que se carguen los resultados
    
    def get_verified_element(self):
        """
        Busca y retorna el primer elemento verificado en los resultados de búsqueda.
        
        Returns:
            WebElement o None: El elemento verificado si se encuentra, None en caso contrario
        """
        # Buscar el RecyclerView que contiene los resultados
        recycler_view = self.wait.until(
            EC.presence_of_element_located((AppiumBy.XPATH, 
                "//androidx.recyclerview.widget.RecyclerView[@resource-id='com.spotify.music:id/search_content_recyclerview']"))
        )
        logger.debug("RecyclerView de resultados encontrado!")
        
        # Buscar todos los ViewGroup con resource-id="com.spotify.music:id/row_root"
        row_elements = recycler_view.find_elements(by=AppiumBy.XPATH, 
            value=".//android.view.ViewGroup[@resource-id='com.spotify.music:id/row_root']")
        num_results = len(row_elements)
        logger.debug(f"Total de elementos row_root encontrados: {num_results}")
        
        # Recorrer los elementos para encontrar el que tenga un ImageView con content-desc="Verified"
        for i, row in enumerate(row_elements):
            try:
                # Buscar el ImageView con content-desc="Verified" dentro de este row
                verified_image = row.find_element(by=AppiumBy.XPATH, 
                    value=".//android.widget.ImageView[@content-desc='Verified']")
                logger.info(f"Elemento verificado encontrado en la posición {i + 1}")
                return row
            except:
                # Si no tiene el ImageView Verified, continuar con el siguiente
                continue
        
        logger.warning("No se encontró ningún elemento con verificación")
        return None
    
    def get_artist_play_button(self):
        """
        Obtiene el botón de play/pause en la página del artista.
        
        Returns:
            WebElement: Elemento del botón de play/pause
        
        Raises:
            TimeoutException: Si no se encuentra el elemento dentro del timeout
        """
        play_pause_button = self.wait.until(
            EC.element_to_be_clickable((AppiumBy.ID, "com.spotify.music:id/button_play_and_pause"))
        )
        logger.info("Botón de play/pause encontrado!")
        return play_pause_button
