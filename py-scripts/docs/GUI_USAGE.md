# Guía de Uso - Interfaz Gráfica (GUI)

## Descripción

La aplicación ahora incluye una interfaz gráfica moderna desarrollada con **CustomTkinter**, diseñada específicamente para Windows. La GUI permite gestionar la automatización de Spotify en múltiples dispositivos Android de forma visual e intuitiva.

## Arquitectura

La aplicación sigue una arquitectura limpia y separada:

```
src/
├── gui/                    # Módulo de interfaz gráfica
│   ├── main_window.py     # Ventana principal
│   ├── components/         # Componentes reutilizables
│   │   └── device_list.py # Lista de dispositivos
│   └── controllers/        # Controladores (MVC)
│       └── app_controller.py
├── services/               # Lógica de negocio
│   └── flow_executor.py   # Servicio de ejecución de flujos
└── gui_app.py             # Punto de entrada para la GUI
```

### Separación de Responsabilidades

- **GUI (`gui/`)**: Solo se encarga de la presentación y la interacción del usuario
- **Controllers (`gui/controllers/`)**: Conectan la GUI con los servicios
- **Services (`services/`)**: Contienen toda la lógica de negocio
- **Flows, Pages, etc.**: Mantienen su funcionalidad original

## Instalación

1. Instalar las dependencias (incluye CustomTkinter):
```bash
pip install -r requirements.txt
```

2. Asegurarse de que Appium Server esté corriendo en `http://127.0.0.1:4723`

3. Conectar dispositivos Android vía ADB

## Ejecución

### Opción 1: Ejecutar desde src/
```bash
cd src
python gui_app.py
```

### Opción 2: Ejecutar desde la raíz
```bash
python src/gui_app.py
```

## Características de la GUI

### Interfaz Principal

- **Título y Descripción**: Identificación clara de la aplicación
- **Controles Superiores**:
  - 🔄 **Refrescar Dispositivos**: Actualiza la lista de dispositivos conectados
  - ▶ **Iniciar Todos**: Inicia flujos en todos los dispositivos disponibles
  - **Campo de Artista**: Permite especificar el nombre del artista a buscar

### Lista de Dispositivos

Cada dispositivo muestra:
- 📱 **ID del Dispositivo**: Identificador único
- **Tipo**: Emulador o Dispositivo Físico
- **Estado**: Estado actual del flujo (Disponible, Iniciando, Ejecutando, Completado, Error)
- **Botones de Acción**:
  - ▶ **Iniciar**: Inicia el flujo para ese dispositivo específico
  - ⏹ **Detener**: Detiene el flujo (si está en ejecución)

### Actualización Automática

- La lista de dispositivos se actualiza automáticamente cada 5 segundos
- Los estados de los flujos se actualizan en tiempo real (cada 1 segundo)
- Los colores cambian según el estado:
  - 🟢 Verde: Completado
  - 🟠 Naranja: Ejecutando/Conectando
  - 🔴 Rojo: Error

## Ventajas de CustomTkinter

1. **Interfaz Moderna**: Apariencia nativa y profesional en Windows
2. **Tema Oscuro**: Incluido por defecto, fácil de personalizar
3. **Ligero**: No requiere dependencias pesadas
4. **Compatible con PyInstaller**: Se puede empaquetar fácilmente
5. **Fácil de Mantener**: Código limpio y bien estructurado

## Personalización

### Cambiar Tema

En `gui/main_window.py`, línea ~30:
```python
ctk.set_appearance_mode("dark")  # Cambiar a "light" para tema claro
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"
```

### Modificar Intervalos de Actualización

En `gui/main_window.py`:
- Actualización de dispositivos: línea ~200 (actualmente 5000ms)
- Actualización de estados: `app_controller.py`, método `start_status_refresh()` (actualmente 1.0s)

## Compilar con PyInstaller

Para crear un ejecutable con la GUI:

```bash
pyinstaller --onefile --name HTB_Spotify_GUI --paths src src/gui_app.py
```

O modificar el archivo `.spec` existente para incluir la GUI.

## Solución de Problemas

### Error: "No module named 'customtkinter'"
```bash
pip install customtkinter
```

### Los dispositivos no aparecen
- Verificar que ADB esté instalado y en el PATH
- Ejecutar `adb devices` en la terminal para verificar conexión
- Presionar el botón "🔄 Refrescar Dispositivos"

### La GUI no responde
- Verificar que Appium Server esté corriendo
- Revisar los logs en `logs/spotify_automation.log`

## Próximas Mejoras Sugeridas

- [ ] Agregar gráficos de progreso por dispositivo
- [ ] Historial de ejecuciones
- [ ] Configuración de parámetros avanzados
- [ ] Exportar logs desde la GUI
- [ ] Notificaciones del sistema cuando completan los flujos

