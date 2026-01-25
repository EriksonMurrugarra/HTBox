"""
Controlador principal que conecta la GUI con los servicios de negocio.
Implementa el patrón MVC para separar la lógica de la presentación.
"""
from services.flow_executor import FlowExecutor
from adb_device_manager import Device
from typing import Callable, Optional
from logger_config import logger
import threading


class AppController:
    """
    Controlador que gestiona la comunicación entre la GUI y los servicios.
    """
    
    def __init__(self):
        """Inicializa el controlador con el ejecutor de flujos"""
        self.flow_executor = FlowExecutor()
        self.status_update_callbacks: list[Callable[[dict[str, str]], None]] = []
        self.refresh_thread: Optional[threading.Thread] = None
        self.refresh_running = False
    
    def get_available_devices(self) -> list[Device]:
        """
        Obtiene la lista de dispositivos disponibles.
        
        Returns:
            Lista de dispositivos conectados
        """
        return self.flow_executor.get_available_devices()
    
    def start_flow_for_device(
        self,
        device_id: str,
        artist_name: str = "Martin Garrix"
    ) -> bool:
        """
        Inicia un flujo para un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
            artist_name: Nombre del artista a buscar
            
        Returns:
            True si se inició correctamente, False en caso contrario
        """
        logger.info(f"[AppController] Iniciando flujo para dispositivo: {device_id}")
        return self.flow_executor.start_flow_for_device(
            device_id=device_id,
            artist_name=artist_name,
            status_callback=self._on_device_status_changed
        )
    
    def start_flows_for_all_devices(self, artist_name: str = "Martin Garrix") -> int:
        """
        Inicia flujos para todos los dispositivos disponibles.
        
        Args:
            artist_name: Nombre del artista a buscar
            
        Returns:
            Número de flujos iniciados
        """
        logger.info(f"[AppController] Iniciando flujos para todos los dispositivos")
        return self.flow_executor.start_flows_for_all_devices(
            artist_name=artist_name,
            status_callback=self._on_device_status_changed
        )
    
    def stop_flow_for_device(self, device_id: str):
        """
        Detiene un flujo para un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
        """
        logger.info(f"[AppController] Deteniendo flujo para dispositivo: {device_id}")
        # Nota: En una implementación más completa, aquí se podría
        # implementar un mecanismo para detener el flujo de forma segura
        # Por ahora, los hilos son daemon y se cerrarán cuando termine la app
    
    def get_device_statuses(self) -> dict[str, str]:
        """
        Obtiene el estado de todos los dispositivos.
        
        Returns:
            Diccionario con device_id -> status
        """
        devices = self.get_available_devices()
        statuses = {}
        for device in devices:
            statuses[device.device_id] = self.flow_executor.get_device_status(device.device_id)
        return statuses
    
    def register_status_update_callback(self, callback: Callable[[dict[str, str]], None]):
        """
        Registra un callback para recibir actualizaciones de estado.
        
        Args:
            callback: Función que será llamada con un diccionario de estados (device_id -> status)
        """
        self.status_update_callbacks.append(callback)
    
    def _on_device_status_changed(self, device_id: str, status: str):
        """
        Callback interno cuando cambia el estado de un dispositivo.
        Notifica a todos los callbacks registrados.
        
        Args:
            device_id: ID del dispositivo
            status: Nuevo estado
        """
        statuses = self.get_device_statuses()
        for callback in self.status_update_callbacks:
            try:
                callback(statuses)
            except Exception as e:
                logger.error(f"Error en callback de actualización de estado: {e}")
    
    def start_status_refresh(self, interval: float = 1.0):
        """
        Inicia un hilo que actualiza periódicamente los estados.
        
        Args:
            interval: Intervalo en segundos entre actualizaciones
        """
        if self.refresh_running:
            return
        
        self.refresh_running = True
        
        def refresh_loop():
            import time
            while self.refresh_running:
                statuses = self.get_device_statuses()
                for callback in self.status_update_callbacks:
                    try:
                        callback(statuses)
                    except Exception as e:
                        logger.error(f"Error en callback de refresh: {e}")
                time.sleep(interval)
        
        self.refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_thread.start()
    
    def stop_status_refresh(self):
        """Detiene el hilo de actualización de estados"""
        self.refresh_running = False

