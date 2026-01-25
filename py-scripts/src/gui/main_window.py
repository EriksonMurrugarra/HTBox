"""
Ventana principal de la aplicación GUI.
Utiliza CustomTkinter para una interfaz moderna y amigable.
"""
import customtkinter as ctk
from gui.components.device_list import DeviceListFrame
from gui.controllers.app_controller import AppController
from adb_device_manager import Device
from logger_config import logger
from typing import Optional
import threading


class MainWindow(ctk.CTk):
    """
    Ventana principal de la aplicación de automatización de Spotify.
    """
    
    def __init__(self):
        """Inicializa la ventana principal"""
        super().__init__()
        
        # Configuración de la ventana
        self.title("HTBox - Spotify Automation")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Configurar tema de CustomTkinter
        ctk.set_appearance_mode("dark")  # "dark" o "light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Controlador
        self.controller = AppController()
        self.controller.register_status_update_callback(self._on_statuses_updated)
        
        # Crear interfaz
        self._create_widgets()
        
        # Iniciar actualización periódica
        self.controller.start_status_refresh(interval=1.0)
        
        # Cargar dispositivos iniciales
        self._refresh_devices()
        
        # Actualizar periódicamente la lista de dispositivos
        self._schedule_device_refresh()
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # Frame principal con padding
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎵 Spotify Automation",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Gestiona la automatización de Spotify en múltiples dispositivos Android",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Frame de controles superiores
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botón de refrescar dispositivos
        refresh_button = ctk.CTkButton(
            controls_frame,
            text="🔄 Refrescar Dispositivos",
            command=self._refresh_devices,
            width=200
        )
        refresh_button.pack(side="left", padx=10, pady=10)
        
        # Botón de iniciar todos
        start_all_button = ctk.CTkButton(
            controls_frame,
            text="▶ Iniciar Todos",
            command=self._start_all_flows,
            width=200,
            fg_color="green",
            hover_color="darkgreen"
        )
        start_all_button.pack(side="left", padx=10, pady=10)
        
        # Campo de artista
        artist_frame = ctk.CTkFrame(controls_frame)
        artist_frame.pack(side="left", padx=10, pady=10)
        
        artist_label = ctk.CTkLabel(artist_frame, text="Artista:")
        artist_label.pack(side="left", padx=(0, 5))
        
        self.artist_entry = ctk.CTkEntry(
            artist_frame,
            placeholder_text="Martin Garrix",
            width=150
        )
        self.artist_entry.pack(side="left")
        self.artist_entry.insert(0, "Martin Garrix")
        
        # Frame para la lista de dispositivos
        devices_label = ctk.CTkLabel(
            main_frame,
            text="Dispositivos Conectados",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        devices_label.pack(anchor="w", padx=20, pady=(10, 5))
        
        # Lista de dispositivos (scrollable)
        self.device_list = DeviceListFrame(main_frame)
        self.device_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.device_list.set_callbacks(
            on_start=self._on_device_start,
            on_stop=self._on_device_stop
        )
        
        # Frame de estado inferior
        status_frame = ctk.CTkFrame(main_frame)
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Listo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.status_label.pack(pady=10)
    
    def _refresh_devices(self):
        """
        Refresca la lista de dispositivos disponibles.
        """
        try:
            devices = self.controller.get_available_devices()
            statuses = self.controller.get_device_statuses()
            
            self.device_list.update_devices(devices, statuses)
            
            device_count = len(devices)
            self.status_label.configure(
                text=f"Dispositivos encontrados: {device_count}",
                text_color="white"
            )
            
            logger.info(f"[MainWindow] Dispositivos refrescados: {device_count}")
        except Exception as e:
            logger.error(f"[MainWindow] Error al refrescar dispositivos: {e}", exc_info=True)
            self.status_label.configure(
                text=f"Error al refrescar dispositivos: {str(e)}",
                text_color="red"
            )
    
    def _schedule_device_refresh(self):
        """
        Programa la actualización periódica de la lista de dispositivos.
        """
        self._refresh_devices()
        # Programar siguiente actualización en 5 segundos
        self.after(5000, self._schedule_device_refresh)
    
    def _on_statuses_updated(self, statuses: dict[str, str]):
        """
        Callback cuando se actualizan los estados de los dispositivos.
        Solo actualiza los estados, no modifica la lista de dispositivos.
        
        Args:
            statuses: Diccionario con device_id -> status
        """
        # Solo actualizar los estados de los dispositivos existentes
        # No llamar a update_devices() completo para evitar duplicados
        self.device_list.update_device_statuses(statuses)
    
    def _on_device_start(self, device_id: str):
        """
        Maneja el inicio de un flujo para un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
        """
        artist_name = self.artist_entry.get().strip() or "Martin Garrix"
        
        if self.controller.start_flow_for_device(device_id, artist_name):
            self.status_label.configure(
                text=f"Flujo iniciado para dispositivo: {device_id}",
                text_color="green"
            )
        else:
            self.status_label.configure(
                text=f"Error: El dispositivo {device_id} ya está en ejecución",
                text_color="orange"
            )
    
    def _on_device_stop(self, device_id: str):
        """
        Maneja la detención de un flujo para un dispositivo específico.
        
        Args:
            device_id: ID del dispositivo
        """
        self.controller.stop_flow_for_device(device_id)
        self.status_label.configure(
            text=f"Deteniendo flujo para dispositivo: {device_id}",
            text_color="orange"
        )
    
    def _start_all_flows(self):
        """Inicia flujos para todos los dispositivos disponibles"""
        artist_name = self.artist_entry.get().strip() or "Martin Garrix"
        count = self.controller.start_flows_for_all_devices(artist_name)
        
        self.status_label.configure(
            text=f"Flujos iniciados para {count} dispositivo(s)",
            text_color="green"
        )
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        logger.info("[MainWindow] Cerrando aplicación...")
        self.controller.stop_status_refresh()
        self.destroy()

