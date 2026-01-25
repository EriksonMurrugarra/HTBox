#!/bin/bash
# Script para compilar usando el archivo .spec para Linux

set -e

echo "=== Compilando para Linux usando HTB_Spotify_001.spec ==="
echo ""

# Nombre de la imagen Docker
IMAGE_NAME="spotify-automation-builder"
CONTAINER_NAME="spotify-builder-$$"

# Construir imagen Docker si no existe
if ! docker images | grep -q "$IMAGE_NAME"; then
    echo "Construyendo imagen Docker..."
    docker build -f Dockerfile.build -t $IMAGE_NAME .
fi

# Crear contenedor y compilar usando el archivo .spec
echo "Compilando ejecutable para Linux usando .spec..."
docker run --name $CONTAINER_NAME $IMAGE_NAME pyinstaller HTB_Spotify_001.spec

# Crear directorio de salida si no existe
mkdir -p dist-linux

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
