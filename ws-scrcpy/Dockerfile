# Dockerfile para construir ws-scrcpy en Linux
# Solo para construcción, no para ejecución

FROM node:18-bullseye-slim

# Instalar herramientas de compilación necesarias para módulos nativos
RUN apt-get update && apt-get install -y \
    build-essential \
    python3 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivos de configuración de dependencias
COPY package*.json ./
COPY tsconfig.json ./

# Instalar dependencias (incluyendo devDependencies para el build)
RUN npm install

# Copiar código fuente y archivos de configuración
COPY . .

# Construir el proyecto
RUN npm run dist

# Verificar que dist/ se creó correctamente
RUN test -d dist && test -f dist/index.js && echo "Build successful"

# El directorio dist/ quedará disponible para copiar fuera del contenedor
