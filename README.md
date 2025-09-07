# WhatsApp Viewer

Una herramienta en Python y Streamlit para visualizar, filtrar y explorar tus chats exportados de WhatsApp, incluyendo mensajes y archivos multimedia.

## Características
- Visualiza mensajes y archivos multimedia de tus chats exportados.
- Filtra mensajes por fecha, texto, mayúsculas/minúsculas y coincidencia exacta de palabra.
- Visualiza imágenes, reproduce videos y audios, y descarga archivos multimedia.
- Interfaz web sencilla y rápida con Streamlit.

## Requisitos
- Python 3.8 o superior
- Streamlit (`pip install streamlit`)

## Cómo usar
1. Coloca los archivos `.zip` exportados de tus chats de WhatsApp en la carpeta `chats/`.
2. Ejecuta el script principal para extraer los chats:
   ```bash
   python main.py
   ```
3. Inicia la aplicación web:
   ```bash
   streamlit run app.py
   ```
4. Abre el navegador en la dirección que te indique Streamlit y explora tus chats.

## Cómo exportar tus chats de WhatsApp

### En Android
1. Abre WhatsApp y entra al chat que quieres exportar.
2. Toca el menú (tres puntos arriba a la derecha) > Más > Exportar chat.
3. Elige "Incluir archivos" para exportar también fotos, videos y audios.
4. Selecciona cómo quieres enviarte el archivo (puedes usar Google Drive, correo electrónico, etc.).
5. Recibirás un archivo `.zip` que contiene un archivo `.txt` con los mensajes y una carpeta con los archivos multimedia.

### En iPhone
1. Abre WhatsApp y entra al chat que quieres exportar.
2. Toca el nombre del contacto o grupo arriba.
3. Baja y selecciona "Exportar chat".
4. Elige "Adjuntar archivos" para incluir multimedia.
5. Selecciona cómo enviarte el archivo (AirDrop, correo, etc.).

Repite el proceso para cada chat que quieras exportar y coloca los `.zip` en la carpeta `chats/` del proyecto.

---

Proyecto creado con ayuda de GitHub Copilot.
