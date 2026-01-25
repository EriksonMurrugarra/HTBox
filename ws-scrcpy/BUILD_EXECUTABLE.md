# Generar Ejecutable para Linux

Este proyecto está configurado para generar un ejecutable standalone para Linux usando `pkg`.

## Requisitos

1. Node.js instalado (versión 18 o superior recomendada)
2. Las dependencias del proyecto instaladas (`npm install`)

## Pasos para generar el ejecutable

1. **Instalar las dependencias** (si aún no lo has hecho):
   ```bash
   npm install
   ```

2. **Generar el ejecutable**:
   ```bash
   npm run build:linux
   ```

   O también puedes usar:
   ```bash
   npm run build:executable
   ```

3. **El ejecutable se generará en**:
   ```
   dist/ws-scrcpy-linux
   ```

## Uso del ejecutable

Una vez generado, puedes ejecutar el programa directamente:

```bash
./dist/ws-scrcpy-linux
```

O moverlo a cualquier ubicación:

```bash
chmod +x dist/ws-scrcpy-linux
cp dist/ws-scrcpy-linux /usr/local/bin/ws-scrcpy
ws-scrcpy
```

## Notas importantes

- El ejecutable incluye Node.js y todas las dependencias necesarias
- Los archivos estáticos (`public/`, `vendor/`) están incluidos en el ejecutable
- El ejecutable es standalone y no requiere Node.js instalado en el sistema destino
- El tamaño del ejecutable será aproximadamente 50-100MB (incluye Node.js runtime)

## Ejecutar sin ejecutable (solo node dist/index.js)

El proyecto está configurado para incluir **TODAS las dependencias** en el bundle. Esto te permite llevar la carpeta `dist/` a cualquier máquina con Node.js instalado y ejecutarla sin necesidad de instalar dependencias.

**Para usar `node dist/index.js` en cualquier máquina:**

1. **Construir el proyecto**:
   ```bash
   npm run dist
   ```

2. **Copiar la carpeta `dist` completa** a la otra máquina:
   - Debe incluir: `index.js`, `public/`, `vendor/`, `LICENSE`, `package.json`
   - No necesitas copiar `node_modules/`

3. **En la otra máquina, ejecutar directamente**:
   ```bash
   node dist/index.js
   ```

**¡Eso es todo!** No necesitas ejecutar `npm install` en la otra máquina.

**Notas importantes:**
- ✅ Todas las dependencias están incluidas en el bundle (`tslib`, `yaml`, `express`, `ws`, `portfinder`, `@dead50f7/adbkit`, `node-mjpeg-proxy`, `node-pty`, etc.)
- ✅ Las subdependencias también se incluyen automáticamente
- ⚠️ Si encuentras algún módulo faltante después de reconstruir, avísame y lo agregamos
- 💡 Para un paquete aún más portable (sin necesidad de Node.js instalado), usa el ejecutable: `npm run build:linux`

## Solución de problemas

Si encuentras problemas al generar el ejecutable:

1. Asegúrate de que `dist/` contiene todos los archivos necesarios después de ejecutar `npm run dist`
2. Verifica que `pkg` esté instalado: `npx pkg --version`
3. Si hay problemas con assets, verifica que los archivos en `dist/public/` y `dist/vendor/` existan

## Configuración

La configuración de `pkg` está en `dist/package.json`. Si necesitas cambiar la versión de Node.js o agregar más targets, edita la sección `pkg` en ese archivo.

**Nota**: El `dist/package.json` se regenera automáticamente cuando ejecutas `npm run dist`. Si necesitas mantener cambios permanentes en la configuración de `pkg`, considera modificar el proceso de build en `webpack/` o crear un script post-build.
