"""
Componente para mostrar y gestionar la lista de dispositivos
"""
import customtkinter as ctk
from typing import List, Callable, Optional
from adb_device_manager import Device


class DeviceListFrame(ctk.CTkScrollableFrame):
    """
    Frame scrollable que muestra una lista de dispositivos con su estado.
    """
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="#f8f8f8")
        self.device_widgets: dict[str, dict] = {}  # device_id -> {widgets}
        self.on_start_callback: Optional[Callable[[str], None]] = None
        self.on_stop_callback: Optional[Callable[[str], None]] = None
        
    def set_callbacks(
        self,
        on_start: Optional[Callable[[str], None]] = None,
        on_stop: Optional[Callable[[str], None]] = None
    ):
        """
        Establece los callbacks para los botones de inicio/parada.
        
        Args:
            on_start: Callback cuando se presiona el botón de iniciar (device_id)
            on_stop: Callback cuando se presiona el botón de detener (device_id)
        """
        self.on_start_callback = on_start
        self.on_stop_callback = on_stop
    
    def update_devices(self, devices: List[Device], device_statuses: dict[str, str] = None):
        """
        Actualiza la lista de dispositivos mostrados.
        
        Args:
            devices: Lista de dispositivos a mostrar
            device_statuses: Diccionario con el estado de cada dispositivo (device_id -> status)
        """
        if device_statuses is None:
            device_statuses = {}
        
        # Obtener IDs de dispositivos actuales (eliminar duplicados por si acaso)
        current_device_ids = set(device.device_id for device in devices)
        existing_device_ids = set(self.device_widgets.keys())
        
        # Eliminar widgets de dispositivos que ya no están disponibles
        for device_id in existing_device_ids - current_device_ids:
            self._remove_device_widget(device_id)
        
        # Agregar o actualizar widgets de dispositivos
        # Usar un set para rastrear dispositivos procesados y evitar duplicados
        processed_ids = set()
        for device in devices:
            device_id = device.device_id
            
            # Verificación adicional: saltar si ya procesamos este dispositivo
            if device_id in processed_ids:
                continue
            processed_ids.add(device_id)
            
            status = device_statuses.get(device_id, "Disponible")
            
            # Verificación doble antes de crear widget
            if device_id not in self.device_widgets:
                self._create_device_widget(device, status)
            else:
                # Solo actualizar el estado si el widget ya existe
                self._update_device_widget(device_id, status)
    
    def _create_device_widget(self, device: Device, status: str):
        """
        Crea los widgets para un nuevo dispositivo.
        
        Args:
            device: Dispositivo a mostrar
            status: Estado inicial del dispositivo
        """
        device_id = device.device_id
        
        # Frame principal para el dispositivo (card blanca estilo Spotify)
        device_frame = ctk.CTkFrame(
            self,
            fg_color="white",
            corner_radius=8
        )
        device_frame.pack(fill="x", padx=5, pady=5)
        
        # Información del dispositivo
        info_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # ID del dispositivo
        device_label = ctk.CTkLabel(
            info_frame,
            text=f"📱 {device_id}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#191414"
        )
        device_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Tipo (Emulador o Físico)
        device_type = "Emulador" if device.is_emulator else "Dispositivo Físico"
        type_label = ctk.CTkLabel(
            info_frame,
            text=device_type,
            font=ctk.CTkFont(size=11),
            text_color="#535353"
        )
        type_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Estado
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Estado: {status}",
            font=ctk.CTkFont(size=11),
            text_color="#191414"
        )
        status_label.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botones de acción (colores tecnológicos)
        buttons_frame = ctk.CTkFrame(device_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=5, pady=5)
        
        start_button = ctk.CTkButton(
            buttons_frame,
            text="▶ Iniciar",
            width=100,
            fg_color="#1DB954",
            hover_color="#1ed760",
            text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._on_start_clicked(device_id) if self.on_start_callback else None
        )
        start_button.pack(side="left", padx=5)
        
        stop_button = ctk.CTkButton(
            buttons_frame,
            text="⏹ Detener",
            width=100,
            fg_color="#535353",
            hover_color="#404040",
            text_color="white",
            font=ctk.CTkFont(size=12),
            command=lambda: self._on_stop_clicked(device_id) if self.on_stop_callback else None
        )
        stop_button.pack(side="left", padx=5)
        
        # Guardar referencias
        self.device_widgets[device_id] = {
            "frame": device_frame,
            "status_label": status_label,
            "start_button": start_button,
            "stop_button": stop_button
        }
    
    def update_device_statuses(self, device_statuses: dict[str, str]):
        """
        Actualiza solo los estados de los dispositivos existentes.
        No crea nuevos widgets, solo actualiza los existentes.
        
        Args:
            device_statuses: Diccionario con device_id -> status
        """
        for device_id, status in device_statuses.items():
            if device_id in self.device_widgets:
                self._update_device_widget(device_id, status)
    
    def _update_device_widget(self, device_id: str, status: str):
        """
        Actualiza el estado de un dispositivo existente.
        
        Args:
            device_id: ID del dispositivo
            status: Nuevo estado
        """
        if device_id not in self.device_widgets:
            return
        
        widgets = self.device_widgets[device_id]
        widgets["status_label"].configure(text=f"Estado: {status}")
        
        # Cambiar color del estado según el estado actual (colores tecnológicos)
        if "Error" in status:
            widgets["status_label"].configure(text_color="#e22134")
        elif "Completado" in status or "✅" in status:
            widgets["status_label"].configure(text_color="#1DB954")
        elif "Ejecutando" in status or "Conectando" in status:
            widgets["status_label"].configure(text_color="#ff6b35")
        else:
            widgets["status_label"].configure(text_color="#191414")
    
    def _remove_device_widget(self, device_id: str):
        """
        Elimina los widgets de un dispositivo.
        
        Args:
            device_id: ID del dispositivo a eliminar
        """
        if device_id in self.device_widgets:
            widgets = self.device_widgets[device_id]
            widgets["frame"].destroy()
            del self.device_widgets[device_id]
    
    def _on_start_clicked(self, device_id: str):
        """Maneja el clic en el botón de iniciar"""
        if self.on_start_callback:
            self.on_start_callback(device_id)
    
    def _on_stop_clicked(self, device_id: str):
        """Maneja el clic en el botón de detener"""
        if self.on_stop_callback:
            self.on_stop_callback(device_id)

