"""
Configuración centralizada de logging para la aplicación.
Proporciona un logger configurado con formato, niveles y handlers apropiados.
Soporta contexto de device-id por hilo para identificar qué dispositivo emite cada log.
"""
import logging
import sys
import threading
from pathlib import Path
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Contexto local por hilo para almacenar el device_id
_thread_local = threading.local()


def set_device_id(device_id: str):
    """
    Establece el device_id en el contexto del hilo actual.
    
    Args:
        device_id: ID del dispositivo a asociar con el hilo actual
    """
    _thread_local.device_id = device_id


def get_device_id() -> str:
    """
    Obtiene el device_id del contexto del hilo actual.
    
    Returns:
        str: device_id si está establecido, cadena vacía si no
    """
    return getattr(_thread_local, 'device_id', '')


class DeviceContextFormatter(logging.Formatter):
    """
    Formatter personalizado que incluye el device_id en los logs.
    """
    
    def format(self, record):
        """
        Formatea el registro de log incluyendo el device_id si está disponible.
        """
        device_id = get_device_id()
        if device_id:
            # Obtener el mensaje formateado para verificar si ya tiene el device_id
            try:
                message = record.getMessage()
                # Agregar device_id al mensaje si no está ya presente
                if not message.startswith(f'[{device_id}]'):
                    # Si hay argumentos, formatear primero
                    if record.args:
                        formatted_msg = record.msg % record.args if isinstance(record.msg, str) else str(record.msg)
                        record.msg = f'[{device_id}] {formatted_msg}'
                        record.args = ()
                    else:
                        # Si no hay argumentos, simplemente agregar device_id
                        record.msg = f'[{device_id}] {record.msg}'
            except Exception:
                # Si hay algún error, intentar agregar directamente al msg si es string
                if isinstance(record.msg, str) and not record.msg.startswith(f'[{device_id}]'):
                    record.msg = f'[{device_id}] {record.msg}'
        return super().format(record)


def setup_logger(
    name: str = "spotify_automation",
    log_level: int = logging.INFO,
    log_to_file: bool = True,
    log_dir: str = "logs"
) -> logging.Logger:
    """
    Configura y retorna un logger con formato sofisticado.
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Si True, guarda los logs en archivos
        log_dir: Directorio donde guardar los archivos de log
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si el logger ya está configurado
    if logger.handlers:
        return logger
    
    # IMPORTANTE: Prevenir propagación al logger raíz para evitar duplicación
    logger.propagate = False
    
    # Limpiar cualquier handler existente (por si acaso)
    logger.handlers.clear()
    
    logger.setLevel(log_level)
    
    # Formato detallado con timestamp, nivel, módulo, línea y mensaje (incluye device_id)
    detailed_formatter = DeviceContextFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Formato más simple para consola (incluye device_id)
    console_formatter = DeviceContextFormatter(
        fmt='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Handler para consola (stderr)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (si está habilitado)
    if log_to_file:
        # Crear directorio de logs si no existe
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Archivo de log general con rotación
        general_log_file = log_path / f"{name}.log"
        file_handler = RotatingFileHandler(
            general_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Archivo de log diario
        daily_log_file = log_path / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        daily_handler = RotatingFileHandler(
            daily_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=30,  # Mantener 30 días
            encoding='utf-8'
        )
        daily_handler.setLevel(log_level)
        daily_handler.setFormatter(detailed_formatter)
        logger.addHandler(daily_handler)
    
    return logger


# Logger global para uso en toda la aplicación
logger = setup_logger()
