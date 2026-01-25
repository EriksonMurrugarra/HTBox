## Prepare
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

## Empaquetar

### Para macOS (desde macOS)
```shell
./build.sh
# O directamente:
pyinstaller --onefile --name HTB_Spotify_001 --paths src src/main.py
```

### Para Linux (desde macOS/Windows usando Docker)

**Opción 1: Compilar con script automático**
```shell
./build-linux.sh
```

**Opción 2: Compilar usando archivo .spec**
```shell
./build-linux-spec.sh
```

**Opción 3: Compilar manualmente con Docker**
```shell
# Construir imagen
docker build -f Dockerfile.build -t spotify-automation-builder .

# Compilar
docker run --rm -v $(pwd)/dist-linux:/app/dist spotify-automation-builder

# El ejecutable estará en ./dist-linux/HTB_Spotify_001
```

### Nota sobre cross-compilation

PyInstaller **NO soporta cross-compilation** directamente. No puedes compilar un ejecutable para Linux desde macOS o Windows sin usar Docker o una máquina virtual Linux.

La solución recomendada es usar Docker (como se muestra arriba) para compilar dentro de un contenedor Linux.