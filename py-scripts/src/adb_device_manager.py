import subprocess
from dataclasses import dataclass
from typing import List
from logger_config import logger


@dataclass
class Device:
    """Representa un dispositivo Android conectado"""
    device_id: str
    is_emulator: bool


class AdbDeviceManager:
    """Gestiona la comunicación con dispositivos Android a través de ADB"""
    
    @staticmethod
    def get_available_devices(with_logs: bool = False) -> List[Device]:
        """
        Ejecuta 'adb devices' y retorna una lista de objetos Device
        
        Returns:
            List[Device]: Lista de dispositivos disponibles. Cada dispositivo tiene:
                - device_id: ID único del dispositivo
                - is_emulator: True si el dispositivo es un emulador (nombre empieza con 'emulator-')
        
        Example:
            >>> manager = AdbDeviceManager()
            >>> devices = manager.get_available_devices()
            >>> for device in devices:
            ...     print(f"{device.device_id} - Emulator: {device.is_emulator}")
        """
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                check=True
            )
            
            available_devices = []
            lines = result.stdout.strip().split('\n')
            
            # Saltar la primera línea "List of devices attached"
            for line in lines[1:]:
                line = line.strip()
                if line and '\tdevice' in line:
                    # Extraer el device_id (todo antes de '\tdevice')
                    device_id = line.split('\t')[0].strip()
                    if device_id:
                        is_emulator = device_id.startswith('emulator-')
                        available_devices.append(Device(device_id=device_id, is_emulator=is_emulator))
            if with_logs:
                logger.info(f"Dispositivos encontrados: {len(available_devices)}")
                for device in available_devices:
                    logger.debug(f"  - {device.device_id} (emulator: {device.is_emulator})")
            return available_devices
        except subprocess.CalledProcessError as e:
            logger.error(f"Error ejecutando 'adb devices': {e}", exc_info=True)
            return []
        except FileNotFoundError:
            logger.error("Error: 'adb' no se encuentra en el PATH. Asegúrate de que ADB esté instalado.")
            return []
