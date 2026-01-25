#!/bin/bash
# Script para compilar el ejecutable para Linux usando Docker

set -e

echo "=== Compilando para Linux con PyInstaller ==="
echo ""

# Nombre de la imagen Docker
IMAGE_NAME="spotify-automation-builder"
CONTAINER_NAME="spotify-builder-$$"

# Construir imagen Docker si no existe
if ! docker images | grep -q "$IMAGE_NAME"; then
    echo "Construyendo imagen Docker..."
    docker build -f Dockerfile.build -t $IMAGE_NAME .
fi

# Crear contenedor y compilar
echo "Compilando ejecutable para Linux..."
docker run --name $CONTAINER_NAME $IMAGE_NAME pyinstaller --onefile --name HTB_Spotify_001 --paths src src/main.py

# Copiar el ejecutable compilado desde el contenedor
echo "Copiando ejecutable compilado..."
docker cp $CONTAINER_NAME:/app/dist/HTB_Spotify_001 ./dist-linux/HTB_Spotify_001

# Limpiar contenedor
echo "Limpiando..."
docker rm $CONTAINER_NAME

echo ""
echo "✓ Compilación completada!"
echo "Ejecutable Linux disponible en: ./dist-linux/HTB_Spotify_001"
echo ""
echo "Para ejecutarlo en Linux:"
echo "  chmod +x dist-linux/HTB_Spotify_001"
echo "  ./dist-linux/HTB_Spotify_001"
