"""
Servicio para ejecutar flujos de automatización.
Separa la lógica de negocio de la interfaz gráfica.
"""
from appium import webdriver
from appium.options.android import UiAutomator2Options
from adb_device_manager import AdbDeviceManager, Device
from flows.spotify_flow_1 import SpotifyFlow1
from logger_config import logger, set_device_id
from typing import Callable, Optional, Dict
import threading


class FlowExecutor:
    """
    Servicio que gestiona la ejecución de flujos de automatización.
    Permite ejecutar flujos en múltiples dispositivos de forma concurrente.
    """
    
    def __init__(
        self,
        drive_url: str = "http://127.0.0.1:4723",
        app_name: str = "com.spotify.music"
    ):
        """
        Inicializa el ejecutor de flujos.
        
        Args:
            drive_url: URL del servidor Appium
            app_name: Nombre del paquete de la aplicación a automatizar
        """
        self.drive_url = drive_url
        self.app_name = app_name
        self.device_manager = AdbDeviceManager()
        self.active_threads: Dict[str, threading.Thread] = {}
        self.thread_status: Dict[str, str] = {}  # device_id -> status
        self.status_callbacks: Dict[str, Callable] = {}  # device_id -> callback
        
    def get_available_devices(self) -> list[Device]:
        """
        Obtiene la lista de dispositivos disponibles.
        
        Returns:
            Lista de dispositivos conectados
        """
        return self.device_manager.get_available_devices(with_logs=False)
    
    def get_ui_automator_options(self, device_id: str, device_name: str) -> UiAutomator2Options:
        """
        Obtiene las opciones de configuración para un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            device_name: Nombre del dispositivo
            
        Returns:
            Opciones de UiAutomator2 configuradas
        """
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = device_name
        options.udid = device_id
        options.automation_name = "UiAutomator2"
        options.set_capability("noReset", True)
        options.set_capability("dontStopAppOnReset", True)
        options.set_capability("adbExecTimeout", 60000)
        options.set_capability("androidInstallTimeout", 120000)
        return options
    
    def execute_flow_for_device(
        self,
        device_id: str,
        device_name: str = "nophone",
        artist_name: str = "Martin Garrix",
        status_callback: Optional[Callable[[str, str], None]] = None
    ):
        """
        Ejecuta el flujo de Spotify para un dispositivo específico.
        
        Args:
            device_id: ID único del dispositivo
            device_name: Nombre del dispositivo
            artist_name: Nombre del artista a buscar
            status_callback: Función callback para actualizar el estado (device_id, status)
        """
        # Establecer el device_id en el contexto del hilo
        set_device_id(device_id)
        
        def update_status(status: str):
            """Helper para actualizar el estado"""
            self.thread_status[device_id] = status
            if status_callback:
                try:
                    status_callback(device_id, status)
                except Exception as e:
                    logger.error(f"Error en callback de estado: {e}")
        
        update_status("Iniciando...")
        logger.info(f"[FlowExecutor] Iniciando flujo para dispositivo: {device_id}")
        
        # Configuración para conectar con el servidor
        options = self.get_ui_automator_options(device_id, device_name)
        
        # Iniciar el driver
        driver = None
        try:
            update_status("Conectando...")
            driver = webdriver.Remote(self.drive_url, options=options)
            logger.info(f"[FlowExecutor] Driver conectado exitosamente para {device_id}")
            
            update_status("Ejecutando flujo...")
            # Crear y ejecutar el flujo
            flow = SpotifyFlow1(driver, artist_name=artist_name)
            flow.execute()
            
            update_status("Completado ✅")
            logger.info(f"[FlowExecutor] Flujo completado exitosamente para {device_id}")
            
        except Exception as e:
            update_status(f"Error: {str(e)[:50]}")
            logger.error(f"[FlowExecutor] Error durante la ejecución para {device_id}: {e}", exc_info=True)
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info(f"[FlowExecutor] Driver cerrado para {device_id}")
                except Exception as e:
                    logger.error(f"[FlowExecutor] Error al cerrar el driver para {device_id}: {e}", exc_info=True)
            
            # Limpiar el hilo de la lista activa
            if device_id in self.active_threads:
                del self.active_threads[device_id]
            if device_id in self.thread_status:
                # Mantener el estado final por un tiempo
                pass
    
    def start_flow_for_device(
        self,
        device_id: str,
        device_name: str = "nophone",
        artist_name: str = "Martin Garrix",
        status_callback: Optional[Callable[[str, str], None]] = None
    ) -> bool:
        """
        Inicia el flujo en un hilo separado para un dispositivo.
        
        Args:
            device_id: ID único del dispositivo
            device_name: Nombre del dispositivo
            artist_name: Nombre del artista a buscar
            status_callback: Función callback para actualizar el estado
            
        Returns:
            True si el hilo se inició correctamente, False si ya está en ejecución
        """
        if device_id in self.active_threads:
            if self.active_threads[device_id].is_alive():
                logger.warning(f"El flujo para {device_id} ya está en ejecución")
                return False
        
        # Guardar el callback
        if status_callback:
            self.status_callbacks[device_id] = status_callback
        
        # Crear y iniciar el hilo
        thread = threading.Thread(
            target=self.execute_flow_for_device,
            args=(device_id, device_name, artist_name, status_callback),
            name=f"FlowThread-{device_id}",
            daemon=True
        )
        
        self.active_threads[device_id] = thread
        thread.start()
        logger.info(f"[FlowExecutor] Hilo iniciado para dispositivo: {device_id}")
        return True
    
    def start_flows_for_all_devices(
        self,
        artist_name: str = "Martin Garrix",
        status_callback: Optional[Callable[[str, str], None]] = None
    ) -> int:
        """
        Inicia flujos para todos los dispositivos disponibles.
        
        Args:
            artist_name: Nombre del artista a buscar
            status_callback: Función callback para actualizar el estado
            
        Returns:
            Número de hilos iniciados
        """
        devices = self.get_available_devices()
        started_count = 0
        
        for device in devices:
            if self.start_flow_for_device(
                device.device_id,
                device.device_name if hasattr(device, 'device_name') else "nophone",
                artist_name,
                status_callback
            ):
                started_count += 1
        
        return started_count
    
    def get_device_status(self, device_id: str) -> str:
        """
        Obtiene el estado actual de un dispositivo.
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            Estado actual del dispositivo
        """
        return self.thread_status.get(device_id, "No iniciado")
    
    def is_device_running(self, device_id: str) -> bool:
        """
        Verifica si un dispositivo tiene un flujo en ejecución.
        
        Args:
            device_id: ID del dispositivo
            
        Returns:
            True si está en ejecución, False en caso contrario
        """
        if device_id not in self.active_threads:
            return False
        return self.active_threads[device_id].is_alive()
    
    def stop_all_flows(self):
        """
        Detiene todos los flujos en ejecución.
        Nota: Esto solo marca los hilos, no los detiene forzosamente.
        """
        logger.info("[FlowExecutor] Deteniendo todos los flujos...")
        # Los hilos son daemon, se cerrarán cuando termine la aplicación
        self.active_threads.clear()
        self.thread_status.clear()

