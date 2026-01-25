import time
import random
import threading
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from logger_config import logger
from exceptions import AppNotFoundException


class AppPage:
    HOME_KEYCODE = 3
    BACK_KEYCODE = 4
    MENU_KEYCODE = 82
    SEARCH_KEYCODE = 84
    ENTER_KEYCODE = 66
    DEL_KEYCODE = 67
    FORWARD_KEYCODE = 124
    BACKWARD_KEYCODE = 123
    VOLUME_UP_KEYCODE = 24
    VOLUME_DOWN_KEYCODE = 25
    """
    Clase base para páginas de aplicaciones móviles.
    Proporciona métodos genéricos reutilizables.
    """
    
    def __init__(self, driver):
        """
        Inicializa la clase base AppPage.
        
        Args:
            driver: Instancia de WebDriver (Appium)
        """
        self.driver = driver
    
    @staticmethod
    def sleep(seconds: float):
        """
        Pausa la ejecución por el número de segundos especificado.
        
        Args:
            seconds: Número de segundos a esperar (puede ser un float para fracciones de segundo)
        
        Returns:
            None
        """
        time.sleep(seconds)
    
    @staticmethod
    def sleep_random(start_seconds: float, end_seconds: float):
        """
        Pausa la ejecución por un número aleatorio de segundos dentro de un rango.
        
        Args:
            start_seconds: Número mínimo de segundos a esperar (inclusive)
            end_seconds: Número máximo de segundos a esperar (inclusive)
        
        Returns:
            None
        
        Example:
            AppPage.sleep_random(2, 5)  # Espera entre 2 y 5 segundos aleatoriamente
        """
        if start_seconds > end_seconds:
            raise ValueError("start_seconds debe ser menor o igual a end_seconds")
        
        random_seconds = random.uniform(start_seconds, end_seconds)
        time.sleep(random_seconds)
    
    def _is_app_installed_with_timeout(self, app_name, timeout=30):
        """
        Verifica si una app está instalada con un timeout.
        
        Args:
            app_name: Nombre del paquete de la aplicación
            timeout: Timeout en segundos (default: 30)
        
        Returns:
            bool: True si está instalada, False si no o si hay timeout
        """
        result = [None]
        exception_occurred = [False]
        
        def check_installation():
            try:
                result[0] = self.driver.is_app_installed(app_name)
            except Exception as e:
                exception_occurred[0] = True
                result[0] = e
        
        thread = threading.Thread(target=check_installation)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            logger.warning(f"Timeout al verificar si '{app_name}' está instalada después de {timeout}s")
            return False
        
        if exception_occurred[0]:
            logger.error(f"Excepción al verificar instalación: {result[0]}")
            raise result[0]
        
        return result[0]
    
    def go_home(self):
        """
        Presiona el botón HOME del dispositivo Android.
        
        Returns:
            None
        """
        logger.info("Presionando el botón HOME del dispositivo...")
        try:
            self.driver.press_keycode(self.HOME_KEYCODE)
            logger.info("Botón HOME presionado exitosamente")
        except Exception as home_error:
            logger.warning(f"Error al presionar el botón HOME: {home_error}")
    
    def check_banners(self, max_iterations=6, wait_timeout=2, max_total_time=60):
        """
        Verifica y maneja diálogos inesperados, banners y anuncios.
        Ejecuta un bucle de hasta max_iterations iteraciones buscando elementos comunes.
        Tiene un timeout total máximo para evitar que se cuelgue.
        
        Args:
            max_iterations: Número máximo de iteraciones (default: 6)
            wait_timeout: Timeout en segundos para buscar cada elemento (default: 2)
            max_total_time: Tiempo máximo total en segundos (default: 60 = 1 minuto)
        
        Returns:
            bool: True si encontró y manejó algún elemento, False si no encontró nada
        """
        import time as time_module
        
        start_time = time_module.time()
        logger.info(f"Iniciando verificación de banners y diálogos (máximo {max_iterations} iteraciones, timeout total: {max_total_time}s)...")
        
        # Lista de textos a buscar
        texts_to_find = [
            "Continue",
            "Allow",
            "dismiss",
            "Dismiss",
            "Home, Tab 1 of 4"
        ]
        
        # También buscar elementos que contengan "Advertisement"
        advertisement_keywords = ["Advertisement"]
        
        found_and_handled = False
        
        for iteration in range(1, max_iterations + 1):
            # Verificar si hemos excedido el tiempo máximo
            elapsed_time = time_module.time() - start_time
            if elapsed_time >= max_total_time:
                logger.warning(f"Timeout total alcanzado ({max_total_time}s). Deteniendo verificación de banners.")
                break
            
            logger.debug(f"Iteración {iteration}/{max_iterations} de verificación de banners (tiempo transcurrido: {elapsed_time:.1f}s)...")
            element_found = False
            
            # Buscar cada texto en la lista
            for text in texts_to_find:
                # Verificar timeout antes de cada búsqueda
                if time_module.time() - start_time >= max_total_time:
                    logger.warning(f"Timeout total alcanzado durante búsqueda de '{text}'. Deteniendo.")
                    break
                
                try:
                    # Buscar directamente sin wait (instantáneo)
                    xpath = f"//*[@text='{text}' or @content-desc='{text}']"
                    elements = self.driver.find_elements(by=AppiumBy.XPATH, value=xpath) # LIMITAR ELEMENTOS A REVISAR
                    
                    if elements:
                        element = elements[0]
                        try:
                            if element.is_displayed() and element.is_enabled():
                                logger.info(f"Encontrado elemento '{text}'. Tocando...")
                                element.click()
                                logger.info(f"Elemento '{text}' tocado exitosamente")
                                element_found = True
                                found_and_handled = True
                                break
                        except Exception as e:
                            logger.debug(f"Error al interactuar con elemento '{text}': {e}")
                            continue
                except Exception as e:
                    logger.debug(f"Error al buscar el elemento '{text}': {e}")
                    continue
            
            # Si ya encontramos y manejamos un elemento, continuar con la siguiente iteración
            if element_found:
                continue
            
            # Buscar elementos que contengan "Advertisement"
            for keyword in advertisement_keywords:
                # Verificar timeout antes de cada búsqueda
                if time_module.time() - start_time >= max_total_time:
                    logger.warning(f"Timeout total alcanzado durante búsqueda de '{keyword}'. Deteniendo.")
                    break
                
                try:
                    # Buscar directamente sin wait (instantáneo)
                    xpath = f"//*[contains(@text, '{keyword}') or contains(@content-desc, '{keyword}')]"
                    elements = self.driver.find_elements(by=AppiumBy.XPATH, value=xpath)
                    
                    if elements:
                        for element in elements:
                            if time_module.time() - start_time >= max_total_time:
                                break
                            
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    logger.info(f"Encontrado elemento con '{keyword}'. Intentando cerrar...")
                                    
                                    # Intentar encontrar un botón de cerrar cerca del anuncio
                                    close_buttons = ["X", "Close", "✕", "×", "Dismiss"]
                                    closed = False
                                    
                                    for close_text in close_buttons:
                                        if time_module.time() - start_time >= max_total_time:
                                            break
                                        
                                        try:
                                            close_xpath = f".//*[@text='{close_text}' or @content-desc='{close_text}']"
                                            # Buscar directamente sin wait (instantáneo)
                                            close_elements = element.find_elements(by=AppiumBy.XPATH, value=close_xpath)
                                            if close_elements:
                                                close_element = close_elements[0]
                                                if close_element.is_displayed():
                                                    close_element.click()
                                                    logger.info(f"Anuncio cerrado usando botón '{close_text}'")
                                                    closed = True
                                                    found_and_handled = True
                                                    break
                                        except Exception:
                                            continue
                                    
                                    # Si no encontramos botón de cerrar, intentar presionar BACK
                                    if not closed:
                                        logger.info(f"Presionando BACK para cerrar el anuncio...")
                                        self.driver.press_keycode(self.BACK_KEYCODE)
                                        found_and_handled = True
                                    
                                    element_found = True
                                    break
                            except Exception as e:
                                logger.debug(f"Error al procesar elemento de anuncio: {e}")
                                continue
                        
                        if element_found:
                            break
                except Exception as e:
                    logger.debug(f"Error al buscar elementos con '{keyword}': {e}")
                    continue
            
            # Verificar timeout antes de continuar
            if time_module.time() - start_time >= max_total_time:
                logger.warning(f"Timeout total alcanzado. Deteniendo verificación de banners.")
                break
            
            # Si no encontramos nada en esta iteración, continuar inmediatamente
            if not element_found:
                logger.debug(f"No se encontraron elementos en la iteración {iteration}")
        
        elapsed_time = time_module.time() - start_time
        if found_and_handled:
            logger.info(f"Verificación de banners completada en {elapsed_time:.1f}s. Se manejaron algunos elementos.")
        else:
            logger.debug(f"Verificación de banners completada en {elapsed_time:.1f}s. No se encontraron elementos para manejar.")
        
        return found_and_handled
    
    def _close_app_and_go_home(self, app_name, reason=""):
        """
        Cierra la aplicación y vuelve al HOME.
        
        Args:
            app_name: Nombre del paquete de la aplicación
            reason: Razón por la que se está cerrando (para logging)
        
        Returns:
            None
        """
        try:
            if reason:
                logger.debug(f"{reason}")
            self.driver.terminate_app(app_name)
            logger.info(f"Aplicación '{app_name}' cerrada exitosamente")
            self.sleep_random(3, 5)
            self.go_home()
        except Exception as e:
            logger.debug(f"No se pudo cerrar la app '{app_name}' (puede que no esté abierta): {e}")
    
    def stop_app_if_opened(self, app_name):
        """
        Detiene la aplicación si está abierta.
        
        Args:
            app_name: Nombre del paquete de la aplicación
        
        Returns:
            None
        """
        try:
            logger.info(f"Verificando si la aplicación '{app_name}' está abierta...")
            
            # Verificar el paquete actual para ver si la app está en primer plano
            try:
                current_package = self.driver.current_package
                if current_package == app_name:
                    logger.info(f"La aplicación '{app_name}' está abierta. Cerrando...")
                    self._close_app_and_go_home(app_name)
                elif current_package is None:
                    logger.debug(f"No se pudo obtener el paquete actual, intentando cerrar la app de todas formas...")
                    self._close_app_and_go_home(app_name, "Intentando cerrar la app sin verificación de paquete")
                else:
                    logger.debug(f"La aplicación '{app_name}' no está en primer plano (paquete actual: {current_package})")
                    # Aún así intentar cerrarla por si está en segundo plano
                    self._close_app_and_go_home(app_name, f"App no está en primer plano, cerrando de todas formas")
            except Exception as e:
                logger.warning(f"Error al verificar el paquete actual antes de cerrar la app: {e}")
                # Intentar cerrar de todas formas
                self._close_app_and_go_home(app_name, "Error al verificar paquete, intentando cerrar de todas formas")
                    
        except Exception as e:
            logger.warning(f"Error inesperado al intentar cerrar la aplicación '{app_name}': {e}")
            # No lanzar excepción, solo loguear el error y continuar
    
    def open_app(self, app_name):
        """
        Abre o activa una aplicación Android.
        
        Args:
            app_name: Nombre del paquete de la aplicación
        
        Returns:
            None
        
        Raises:
            AppNotFoundException: Si la aplicación no está instalada o no puede ser abierta
        """
        logger.info(f"Abriendo/activando la aplicación: {app_name}")
        
        # Cerrar la aplicación si está abierta antes de intentar abrirla
        
        try:
            # Verificar si la aplicación está instalada
            logger.info(f"Verificando si la aplicación '{app_name}' está instalada...")
            try:
                is_installed = self._is_app_installed_with_timeout(app_name, timeout=30)
                logger.info(f"Resultado de verificación de instalación: {is_installed}")
            except Exception as e:
                logger.error(f"Error al verificar si la app está instalada: {e}", exc_info=True)
                raise AppNotFoundException(app_name, f"Error al verificar si la aplicación '{app_name}' está instalada: {str(e)}")
            
            if not is_installed:
                logger.error(f"La aplicación '{app_name}' no está instalada")
                raise AppNotFoundException(app_name, f"La aplicación '{app_name}' no está instalada")
            

            self.stop_app_if_opened(app_name)
        
            self.sleep_random(2, 5)

            # Intentar activar la aplicación
            logger.info(f"Activando la aplicación '{app_name}'...")
            try:
                self.driver.activate_app(app_name)
                logger.info(f"Comando activate_app ejecutado para '{app_name}'")
            except Exception as e:
                logger.error(f"Error al ejecutar activate_app: {e}", exc_info=True)
                raise AppNotFoundException(app_name, f"Error al activar la aplicación '{app_name}': {str(e)}")
            
            # Esperar un momento para que la app se active completamente
            logger.info("Esperando a que la aplicación se active...")
            self.sleep(3)
            
            # Verificar el paquete actual (pero no fallar si no coincide exactamente)
            logger.info("Verificando el paquete actual...")
            try:
                current_package = self.driver.current_package
                logger.info(f"Paquete actual detectado: {current_package}")
                
                if current_package == app_name:
                    logger.info(f"Aplicación {app_name} activada/abierta correctamente (paquete confirmado)")
                elif current_package is None:
                    logger.warning(f"No se pudo obtener el paquete actual, pero la app debería estar activa")
                    logger.info(f"Aplicación {app_name} activada (verificación de paquete no disponible)")
                else:
                    logger.warning(f"El paquete actual ({current_package}) no coincide con el esperado ({app_name})")
                    # Intentar una vez más con más tiempo
                    logger.info("Intentando activar la aplicación nuevamente...")
                    try:
                        self.driver.activate_app(app_name)
                        logger.info("Segundo intento de activate_app completado")
                        self.sleep(3)
                    except Exception as e:
                        logger.warning(f"Error en el segundo intento de activate_app: {e}")
                    
                    try:
                        current_package = self.driver.current_package
                        if current_package == app_name:
                            logger.info(f"Aplicación {app_name} activada/abierta correctamente después del segundo intento")
                        elif current_package is None:
                            logger.warning(f"No se pudo verificar el paquete después del segundo intento, pero continuando...")
                            logger.info(f"Aplicación {app_name} activada (asumiendo éxito)")
                        else:
                            logger.warning(f"El paquete sigue siendo diferente ({current_package}), pero continuando con la ejecución")
                            logger.info(f"Aplicación {app_name} activada (advertencia: paquete diferente)")
                    except Exception as e:
                        logger.warning(f"Error al verificar el paquete después del segundo intento: {e}")
                        logger.info(f"Aplicación {app_name} activada (no se pudo verificar, pero continuando)")
                        
            except Exception as e:
                logger.warning(f"Error al verificar el paquete actual después de activar la app: {e}", exc_info=True)
                logger.info(f"Aplicación {app_name} activada (no se pudo verificar el paquete, pero continuando)")
                        
            logger.info(f"open_app completado para {app_name}")
            # self.check_banners()
            
        except AppNotFoundException:
            # Re-lanzar la excepción personalizada
            logger.error(f"AppNotFoundException lanzada para {app_name}")
            raise
        except Exception as e:
            # Capturar cualquier otra excepción y convertirla en AppNotFoundException
            logger.error(f"Error inesperado al abrir la aplicación '{app_name}': {e}", exc_info=True)
            raise AppNotFoundException(app_name, f"Error al abrir la aplicación '{app_name}': {str(e)}")