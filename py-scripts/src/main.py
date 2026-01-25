from appium import webdriver
from appium.options.android import UiAutomator2Options
from adb_device_manager import AdbDeviceManager
from flows.spotify_flow_1 import SpotifyFlow1
from logger_config import logger, set_device_id
import threading

drive_url = "http://127.0.0.1:4723"
app_name = "com.spotify.music"
app_activity = "com.spotify.music.MainActivity"

device_manager = AdbDeviceManager()

# ------------------------------------------------------------

available_devices = device_manager.get_available_devices(with_logs=False)


def get_ui_automator_options(device_id: str, device_name: str):
    """
    Obtiene las opciones de configuración para un dispositivo específico.
    """
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.device_name = device_name
    options.udid = device_id
    options.automation_name = "UiAutomator2"
    options.set_capability("noReset", True)  # Importante para no perder el login
    options.set_capability("dontStopAppOnReset", True)  # No detener la app al resetear
    options.set_capability("adbExecTimeout", 60000)  # 60 segundos en milisegundos
    options.set_capability("androidInstallTimeout", 120000)  # 120 segundos para instalación
    return options

def execute_flow_for_device(device_id: str, device_name: str):
    """
    Ejecuta el flujo 1 de Spotify para un dispositivo específico.
    
    Args:
        device_id: ID único del dispositivo (UDID)
        device_name: Nombre del dispositivo
    """
    # Establecer el device_id en el contexto del hilo
    set_device_id(device_id)
    logger.info(f"[main] [execute_flow_for_device] Iniciando flujo...")
    
    # Configuración para conectar con el servidor
    options = get_ui_automator_options(device_id, device_name)
    
    # Iniciar el driver
    driver = None
    try:
        driver = webdriver.Remote(drive_url, options=options)
        logger.info(f"[main] [execute_flow_for_device] Driver conectado exitosamente")
        # Crear y ejecutar el flujo
        flow = SpotifyFlow1(driver, artist_name="Martin Garrix")
        flow.execute()
        
        logger.info(f"[main] [execute_flow_for_device] Flujo completado exitosamente ✅")
        
    except Exception as e:
        logger.error(f"[main] [execute_flow_for_device] Error durante la ejecución: ❌: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logger.info(f"[main] [execute_flow_for_device] Driver cerrado")
            except Exception as e:
                logger.error(f"[main] [execute_flow_for_device] Error al cerrar el driver: {e}", exc_info=True)


# Crear y ejecutar hilos para cada dispositivo
threads = []
for device in available_devices:
    thread = threading.Thread(
        target=execute_flow_for_device,
        args=(device.device_id, "nophone"),
        name=f"Thread-{device.device_id}"
    )
    threads.append(thread)
    thread.start()
    logger.info(f"[main] Iniciado hilo para dispositivo: {device.device_id}")

# Esperar a que todos los hilos terminen
logger.info(f"[main] Esperando a que {len(threads)} hilos terminen...")
logger.info(f"[main] ********************************************************")
for thread in threads:
    thread.join()
    logger.info(f"[main] Hilo {thread.name} finalizado")

logger.info("[main] Todos los flujos han finalizado.")

# Flujo.
# ejecutar 100/200 dispositivos en ese momento, uno inicia luego de X segundos, ramdom.
# ejecucion diferente, cada paso demora X delay.
# ejecutar musica de manera random. 
# Pasos diferentes. 
# Tiempo de ejecucion de automatizacion. Todo se cierra a X momento. 
# Trust y Boost de spotify. 
# Docker run

# To execute
# scrcpy --serial R5CT227FYRV