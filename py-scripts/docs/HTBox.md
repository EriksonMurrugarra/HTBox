
appium --address 0.0.0.0


## Installing HTBox

### 1. Instalar ADB (Android Debug Bridge)

En Linux/Raspberry Pi, instalar ADB es muy sencillo porque está en los repositorios oficiales.

```bash
sudo apt update
sudo apt install -y android-tools-adb android-tools-fastboot

```

**Para verificar:** Conecta un teléfono por USB y ejecuta `adb devices`. Deberías ver el número de serie del dispositivo.

---

### 2. Instalar Node.js y NPM

Appium corre sobre Node.js. No uses la versión que viene por defecto en `apt` (suele ser muy antigua). Recomiendo usar **nvm** para instalar una versión estable (LTS).

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20

```

---

### 3. Instalar Java (Necesario para Android)

Appium necesita Java para interactuar con los frameworks de automatización de Android.

```bash
sudo apt install -y default-jdk-headless

```

Verifica la instalación con `java -version`.


# Creamos la carpeta del SDK en tu home
mkdir -p ~/android-sdk/platform-tools

# Creamos un enlace simbólico de tu ADB real a esa carpeta
ln -s /usr/bin/adb ~/android-sdk/platform-tools/adb



nano ~/.bashrc


export ANDROID_HOME=$HOME/android-sdk
export ANDROID_SDK_ROOT=$HOME/android-sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools

---

### 4. Instalar Appium Server

Ahora instalamos el servidor de Appium y el driver específico para Android (**UIAutomator2**).

```bash
# Instalar Appium globalmente
npm install -g appium

# Instalar el driver de Android
appium driver install uiautomator2

```

---

### 5. Configurar Variables de Entorno

Para que Appium sepa dónde están Java y el SDK, debes editar tu archivo `.bashrc` o `.zshrc`:

```bash
nano ~/.bashrc

```

Añade estas líneas al final:

```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64  # Ajusta si tu versión varía
export PATH=$PATH:$JAVA_HOME/bin

```

Guarda y recarga: `source ~/.bashrc`.

---

### 6. Ejecutar el Servidor

Para iniciar Appium permitiendo conexiones externas (desde tu script de Python en otra PC o desde la misma Pi):

```bash
appium --address 0.0.0.0

```

---

### Retos técnicos en Raspberry Pi (ARM)

1. **Potencia:** Si usas una **Raspberry Pi 3**, podrías notar lentitud si las pruebas son muy pesadas. La **Raspberry Pi 4 o 5** con al menos 4GB de RAM son ideales.
2. **Drivers USB:** Asegúrate de que el cable USB sea de buena calidad. Las Raspberry Pi a veces tienen limitaciones de energía en los puertos USB si alimentas muchos dispositivos a la vez (un Hub USB con alimentación externa es recomendable).
3. **Appium Inspector:** No podrás correr la interfaz gráfica de Appium Inspector de forma fluida en la Pi. Lo ideal es correr el **Server** en la Pi y usar el **Inspector** en tu PC apuntando a la IP de la Raspberry.

## Troubleshoot

npm install -g appium-doctor
appium-doctor --android


appium driver uninstall uiautomator2
appium driver install uiautomator2