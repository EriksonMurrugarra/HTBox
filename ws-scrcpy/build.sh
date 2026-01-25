#!/bin/bash
set -e

# Script para construir ws-scrcpy usando Docker (Linux)
# Esto asegura que los módulos nativos se compilen correctamente para Linux

IMAGE_NAME="ws-scrcpy-builder"
CONTAINER_NAME="ws-scrcpy-builder-temp"
OUTPUT_DIR="./dist-linux"

echo "🚀 Construyendo ws-scrcpy para Linux usando Docker..."
echo ""

# Limpiar contenedor temporal si existe
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "🧹 Limpiando contenedor temporal existente..."
    docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true
fi

# Construir la imagen Docker
echo "📦 Construyendo imagen Docker..."
docker build -t ${IMAGE_NAME}:latest .

if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen Docker"
    exit 1
fi

echo "✅ Imagen construida exitosamente"
echo ""

# Crear contenedor temporal
echo "📦 Creando contenedor temporal..."
docker create --name ${CONTAINER_NAME} ${IMAGE_NAME}:latest

if [ $? -ne 0 ]; then
    echo "❌ Error al crear el contenedor"
    exit 1
fi

# Limpiar directorio de salida si existe
if [ -d "${OUTPUT_DIR}" ]; then
    echo "🧹 Limpiando directorio de salida existente..."
    rm -rf ${OUTPUT_DIR}
fi

# Extraer archivos dist/ del contenedor
echo "📤 Extrayendo archivos construidos..."
docker cp ${CONTAINER_NAME}:/app/dist ${OUTPUT_DIR}

if [ $? -ne 0 ]; then
    echo "❌ Error al extraer archivos del contenedor"
    docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true
    exit 1
fi

# Limpiar contenedor temporal
echo "🧹 Limpiando contenedor temporal..."
docker rm -f ${CONTAINER_NAME} > /dev/null 2>&1 || true

# Verificar que los archivos se extrajeron correctamente
if [ ! -d "${OUTPUT_DIR}" ] || [ ! -f "${OUTPUT_DIR}/index.js" ]; then
    echo "❌ Error: Los archivos no se extrajeron correctamente"
    exit 1
fi

echo ""
echo "✅ ¡Construcción completada exitosamente!"
echo ""
echo "📁 Archivos construidos disponibles en: ${OUTPUT_DIR}/"
echo ""
echo "Para ejecutar en Linux:"
echo "  cd ${OUTPUT_DIR}"
echo "  node index.js"
echo ""
