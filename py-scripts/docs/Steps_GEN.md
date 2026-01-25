# DESCRIPCIÓN COMPLETA DE LA AUTOMATIZACIÓN DE SPOTIFY

---

## FASE 1: VERIFICACIÓN INICIAL

La automatización comienza verificando si la aplicación de Spotify está instalada en el dispositivo:

- **Si NO está instalada**: Registra un mensaje "App no instalada" y termina el proceso
- **Si SÍ está instalada**: Registra "App instalada" y continúa

---

## FASE 2: PREPARACIÓN DEL DISPOSITIVO

Antes de iniciar Spotify, la automatización prepara el dispositivo:

1. **Detiene Spotify** (si estaba abierta)
2. **Espera 2-3 segundos** (tiempo aleatorio para simular comportamiento humano)
3. **Presiona el botón Home** del dispositivo
4. **Espera 2 segundos**
5. **Busca el botón "Close all"** (cerrar todas las apps recientes):
   - Si lo encuentra: Lo toca para cerrar todas las apps
   - Si no lo encuentra: Vuelve a presionar Home
6. **Espera 3 segundos**

---

## FASE 3: INICIO DE SPOTIFY

1. **Inicia la aplicación Spotify**
2. **Espera 2 segundos** para que cargue

---

## FASE 4: MANEJO DE PERMISOS Y DIÁLOGOS

Ejecuta un bucle de 1 a 6 iteraciones para manejar todos los posibles diálogos:

La app busca simultáneamente estos elementos:

- **"Continue"**: Si aparece, lo toca y sale del bucle
- **"Allow"**: Si aparece (permisos), lo toca y sale del bucle
- **"dismiss"**: Si aparece, lo toca y sale del bucle
- **"Dismiss"**: Si aparece (con mayúscula), lo toca y sale del bucle
- **"Home, Tab 1 of 4"**: Si encuentra la pestaña Home, la toca y continúa

Esta fase asegura que la app esté lista para usar sin interrupciones.

---

## FASE 5: PROCESAMIENTO DE LINKS

Aquí comienza el trabajo principal:

1. **Toma la lista de links** que ingresaste (playlists, artistas o álbumes)
2. **Convierte la lista en un array** separando por líneas
3. **Cuenta cuántos links hay** en total
4. **Registra en logs**:
   - El array completo de links
   - El número total de links
5. **Espera 1 segundo**

---

## FASE 6: BUCLE PRINCIPAL - POR CADA LINK

Para cada link de música, la automatización hace lo siguiente:

### 6.1 Selección del Link

1. **Espera 1 segundo**
2. **Selecciona un link aleatorio** del array
3. **Elimina ese link del array** (para no repetirlo)
4. **Registra**:
   - Los links que quedan pendientes
   - El link que va a reproducir ahora
5. **Espera 2 segundos**

### 6.2 Apertura del Link

1. **Abre el link usando comando ADB** (adb shell am start)
   - Esto abre directamente la playlist/artista/álbum en Spotify
2. **Espera 3-4 segundos** (aleatorio) para que cargue
3. **Desliza hacia arriba** en la pantalla
4. **Espera 2 segundos**
5. **Busca el botón "See more"**:
   - Si existe: Lo toca
   - Si no existe: Continúa de todas formas
6. **Espera 2 segundos**

---

## FASE 7: SELECCIÓN DE CANCIÓN

Aquí depende de la opción que hayas configurado:

### OPCIÓN 1: Reproducir desde la primera canción

Intenta tocar la primera canción con varios métodos:

1. Intenta tocar `row_root` (elemento de fila)
2. Si falla, intenta tocar la primera vista de la composición
3. Si falla, intenta tocar por texto "1"
4. Si falla, intenta tocar otro elemento de la composición
5. Si falla, intenta tocar otro elemento específico
6. Si falla, intenta tocar por coordenadas específicas (389, 1400)

### OPCIÓN 0: Canción aleatoria

1. **Genera un número aleatorio entre 1 y 5**
2. **Registra**: "Elegí canción número X"
3. **Intenta tocar esa canción** en la lista
4. Si falla, **toca la primera canción** como respaldo

---

## FASE 8: INICIO DE REPRODUCCIÓN

Una vez que se toca una canción:

1. **Espera 2 segundos**
2. **Toca la información de la canción** (para expandir detalles)
3. **Calcula cuántas canciones reproducir**:
   - Genera un número aleatorio entre los valores configurados
   - Por ejemplo, si pusiste 10-15, elige un número al azar en ese rango
4. **Registra**: "Número de canciones: X"
5. **Espera 2 segundos**

---

## FASE 9: BUCLE DE CANCIONES

Para cada canción que debe reproducir, hace lo siguiente:

1. **Espera 2 segundos**
2. **Elige una acción aleatoria** (1, 2, 3 o 4):

---

### ACCIÓN 1: Navegar dentro de la canción (25% probabilidad)

Simula que estás viendo la información de la canción:

1. Registra: "Navegar en canción"
2. Espera 1 segundo
3. **Hace 4 deslizamientos hacia arriba**:
   - Desliza (coordenadas: 512, 1680 → 512, 1080)
   - Espera 1 segundo
   - Desliza de nuevo
   - Espera 1 segundo
   - Desliza de nuevo
   - Espera 2 segundo
   - Desliza de nuevo
   - Espera 1 segundo
4. **Espera 2 segundos**
5. **Toca el botón "Previous" o "Next"** (navegar entre canciones)
6. **Espera 25-40 segundos** (el tiempo configurado para "escuchar")

---

### ACCIÓN 2: Navegar en la playlist (25% probabilidad)

Simula que navegas por la lista de canciones:

1. Registra: "Navegar en playlist"
2. Espera 1 segundo
3. **Desliza hacia abajo** (para ver más canciones)
   - Coordenadas: 512, 480 → 512, 1780
4. Espera 3 segundos
5. **Desliza hacia arriba varias veces**
6. Espera 3 segundos
7. **Hace más deslizamientos**
8. Espera 2 segundos
9. **Hace más deslizamientos**
10. Espera 1 segundo
11. **Hace más deslizamientos**
12. Espera 2 segundos
13. **Toca la información de una canción**
14. Espera 3 segundos
15. **Toca "Next"** para cambiar de canción
16. **Espera 25-40 segundos** (tiempo de escucha)

---

### ACCIÓN 3: Navegar por Home (25% probabilidad)

Simula que vas al inicio de Spotify y exploras:

1. Registra: "Navegar en HOME"
2. Espera 1 segundo
3. **Desliza hacia abajo** para ver el feed
4. Espera 3 segundos
5. **Toca la pestaña "Home"**
   - Si no la encuentra, vuelve al inicio del proceso
6. Espera 3 segundos
7. **Hace múltiples deslizamientos** (8 en total)
   - Con pausas entre cada uno
8. **Abre el mismo link de nuevo** usando ADB
9. Espera 3-5 segundos (aleatorio)
10. **Toca la información de una canción**
11. Espera 3-5 segundos
12. **Toca "Next"**
13. **Espera 25-40 segundos**

---

### ACCIÓN 4: Solo esperar (25% probabilidad)

La más simple - solo reproduce:

1. Espera 3-5 segundos (aleatorio)
2. **Toca la información de la canción**
3. Espera 3-5 segundos
4. **Toca "Next"**
5. **Espera 25-40 segundos** (tiempo de escucha)

---

## FASE 10: FINALIZACIÓN DEL BUCLE DE CANCIONES

Después de reproducir todas las canciones configuradas:

1. **Toca "Next"** una última vez
2. **Espera 2 segundos**
3. **Sale del bucle de canciones**

---

## FASE 11: CONTINUAR CON EL SIGUIENTE LINK

1. **Espera 2 segundos**
2. **Sale del bucle de links**
3. **Vuelve a la Fase 6** para procesar el siguiente link

Este proceso se repite hasta que se hayan reproducido todos los links de la lista.

---

## FASE 12: FINALIZACIÓN COMPLETA

Una vez procesados todos los links:

1. **Espera 2 segundos**
2. **Termina la automatización**

---

## RESUMEN DE LOS PARÁMETROS CONFIGURABLES

### 1. Lista de Links
Playlists, artistas o álbumes de Spotify (uno por línea)

### 2. Opción de reproducción
- **Opción 1**: Primera canción
- **Opción 0**: Canción aleatoria

### 3. Tiempo de escucha por canción
- **Mínimo**: 25 segundos (configurable)
- **Máximo**: 40 segundos (configurable)

### 4. Número de canciones por link
- **Mínimo**: 10 canciones (configurable)
- **Máximo**: 15 canciones (configurable)

---

## CARACTERÍSTICAS ESPECIALES

### ✅ Tiempos aleatorios
Simula comportamiento humano con pausas variables

### ✅ Manejo de errores
Múltiples intentos si algo falla (hasta 6 métodos diferentes para tocar elementos)

### ✅ Variedad de acciones
4 tipos diferentes de navegación para parecer más natural

### ✅ Logs detallados
Registra cada paso importante para debugging

### ✅ Selección aleatoria
No reproduce en orden, es más natural y evita patrones detectables

### ✅ Limpieza previa
Cierra apps antes de empezar para evitar interferencias

### ✅ Manejo automático de permisos
Acepta automáticamente diálogos de "Allow", "Continue", "Dismiss", etc.

---

## FLUJO COMPLETO RESUMIDO

```
Inicio
  ↓
¿App instalada? → NO → Fin
  ↓ SÍ
Detener App → Limpiar tareas → Iniciar Spotify
  ↓
Manejar permisos (Loop 1-6 veces)
  ↓
Procesar lista de links
  ↓
Para cada Link (aleatorio):
  ↓
  Abrir link → Seleccionar canción
  ↓
  Para cada canción (10-15):
    ↓
    Acción aleatoria (1-4)
    ↓
    Esperar 25-40 segundos
  ↓
  Siguiente link
↓
Fin
```

---

## TECNOLOGÍA UTILIZADA

- **ADB (Android Debug Bridge)**: Para abrir links directamente
- **XPath**: Para localizar elementos en la interfaz
- **JavaScript**: Para lógica de selección aleatoria
- **Coordenadas táctiles**: Como respaldo cuando falla XPath
- **Gestos de deslizamiento**: Para simular scroll natural

---

## EJEMPLO DE EJECUCIÓN

Si configuras:
- **2 links** en la lista
- **10-15 canciones** por link
- **25-40 segundos** por canción

La automatización:
1. Reproducirá el primer link (aleatorio) con ~12 canciones
2. Cada canción sonará ~32 segundos
3. Cambiará de canción con diferentes patrones de navegación
4. Luego pasará al segundo link
5. Repetirá el proceso
6. **Tiempo total estimado**: 40-80 minutos

---

## NOTAS IMPORTANTES

⚠️ **Requiere permisos ADB**: El dispositivo debe tener depuración USB habilitada

⚠️ **Spotify debe estar instalado**: La app verifica esto primero

⚠️ **Conexión estable**: Los tiempos de espera asumen conexión normal

⚠️ **Interfaz en inglés**: Los textos buscados están en inglés ("Continue", "Allow", etc.)

---

*Automatización creada con GenFarmer - Versión 1.0.0*