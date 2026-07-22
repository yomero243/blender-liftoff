# 🚀 Liftoff — renderiza Blender en la nube (GPU gratis)

**Limpia → Guarda → Renderiza → Despega a la nube.** Un botón purga los datablocks basura, guarda tu `.blend`, renderiza el frame o la animación completa y deja una copia autocontenida en tu carpeta de Google Drive — lista para renderizar gratis con GPU acelerada en [Google Colab](https://colab.research.google.com/github/yomero243/blender-liftoff/blob/main/blender_render.ipynb). Sin OAuth, sin configuraciones complejas.

Flujo diseñado para un **render rápido y gratis**, eliminando datos huérfanos y enviando automáticamente tus renders y proyectos a la nube.

---

## 💎 Ventajas de Utilizar Liftoff

1. ⚡ **GPU de Alta Gama 100% Gratis:** Aprovecha las GPUs NVIDIA de Google Colab (T4 / V100 / A100) para renderizar escenas complejas sin consumir los recursos de tu procesador ni tu tarjeta gráfica local.
2. 🔄 **Cero Configuración de Claves o Red (Sin OAuth):** No requiere crear aplicaciones en Google Cloud API ni configurar tokens OAuth. Todo funciona de forma transparente a través de tu carpeta de **Google Drive para Escritorio**.
3. 🧹 **Archivos más Ligeros y Limpios:** Al purgar automáticamente mallas, materiales y texturas huérfanas antes de subir, tu archivo `.blend` ocupa menos espacio y se transfiere mucho más rápido a la nube.
4. 📦 **Cero Texturas Faltantes (Autocontenido):** Empaqueta de forma automática todas las imágenes y recursos externos dentro del archivo `.blend`, evitando las clásicas texturas en color rosa por rutas rotas.
5. 🛡️ **Chequeo Pre-Vuelo Anti-Errores:** Valida que exista una cámara activa, que no haya cambios sin guardar y que el archivo esté preparado antes de enviarlo a la nube, previniendo fallos y desperdicio de tiempo en Colab.
6. 🎬 **Compatibilidad Cycles + EEVEE Next:** Gracias al entorno gráfico virtual (`xvfb`), puedes renderizar en Colab tanto con Cycles GPU como con EEVEE Next sin cierres repentinos por falta de pantalla.
7. ⚙️ **Ajustes de Render al Vuelo:** Modifica el motor, el porcentaje de resolución o la cantidad de muestras directamente desde el panel del addon sin navegar por menús profundos de Blender.

---

## 🌟 Funciones del Complemento (v1.5.0)

- **Limpiar, Guardar y Renderizar** — ejecuta el flujo completo en un solo clic:
  1. **Limpiar** — purga recursivamente los datablocks huérfanos (mallas, materiales, imágenes, texturas…).
  2. **Guardar** — ejecuta `save_mainfile` sobre el `.blend` actual.
  3. **Renderizar** — renderiza el frame actual o la animación completa con marca de tiempo.
- **🔍 Chequeo Pre-Vuelo (Pre-flight Check)** — diagnostica la escena antes de enviar a la nube.
- **⚙️ Ajustes Rápidos de Render** — modifica desde la pestaña del addon el motor de render (Cycles / EEVEE), porcentaje de resolución, muestras (samples) y Denoiser.
- **Acciones Rápidas** — botones sueltos: Limpiar / Guardar / Render Frame / Render Animación.
- **Abrir Carpeta de Renders** — abre la carpeta de salida (en Google Drive o local) en el explorador de archivos del sistema.
- **Guardar copia en Drive** — empaqueta texturas, comprime el archivo y guarda `<archivo>_cloud.blend` en tu Google Drive.
- **Ir a Colab** — abre el cuaderno de render acelerado por GPU en el navegador.

---

## 📖 Guía Paso a Paso: Cómo Utilizar Liftoff

### Paso 1: Instalación en Blender
1. Descarga el archivo [clean_save_render.py](clean_save_render.py).
2. En Blender, ve a `Editar → Preferencias → Complementos → Instalar…` y selecciona `clean_save_render.py`.
3. Activa la casilla de **"Liftoff — Limpiar · Guardar · Renderizar"**.

### Paso 2: Preparar la Escena en Blender
1. Abre tu panel lateral en la Vista 3D presionando la tecla **`N`** y haz clic en la pestaña **Pipeline**.
2. *(Opcional)* Haz clic en **Chequeo Pre-Vuelo** para verificar que tu escena no tenga errores (cámara activa, guardado, texturas).
3. Haz clic en **Guardar copia en Drive**.
   * Liftoff empaquetará las texturas automáticamente.
   * Generará el archivo `<tu_escena>_cloud.blend` directamente en tu carpeta de Google Drive.

### Paso 3: Renderizar en la Nube con Google Colab
1. En el mismo panel de Blender, haz clic en **Ir a Colab** (abrirá el notebook [`blender_render.ipynb`](https://colab.research.google.com/github/yomero243/blender-liftoff/blob/main/blender_render.ipynb) en tu navegador).
2. En Google Colab:
   * Ve a `Entorno de ejecución → Cambiar tipo de entorno` y selecciona **GPU T4**.
   * Haz clic en `Entorno de ejecución → Ejecutar todo`.
3. Colab auto-detectará tu archivo `*_cloud.blend` más reciente, descargará Blender, activará la GPU y renderizará tu imagen o animación.

### Paso 4: Obtener tus Resultados
* El renderizado aparecerá inmediatamente en pantalla dentro del cuaderno de Colab.
* La imagen o animación se guardará automáticamente en tu Google Drive (`MyDrive/RENDERS/out/`) y se sincronizará de vuelta a tu ordenador en segundos.

---

## 📍 Acceso Rápido en Blender

- **Barra lateral (N)**: Pestaña **Pipeline** en la Vista 3D.
- **Menú Archivo**: Accesos agregados al final de `Archivo`.
- **Atajo de teclado**: `Ctrl+Alt+S` para ejecutar Limpiar, Guardar y Renderizar.

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE).
