import glob
import os
import re
import zipfile
from datetime import datetime

import streamlit as st

CHATS_DIR = 'chats'
OUTPUT_DIR = 'output'

# Crear la carpeta output si no existe
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
# Crear la carpeta chats si no existe
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

# Helper para extraer el nombre del chat del archivo
CHAT_NAME_PATTERN = re.compile(r'Chat de WhatsApp con (.+)\.zip$', re.IGNORECASE)

def get_chat_name(filename, idx):
    match = CHAT_NAME_PATTERN.search(filename)
    if match:
        return match.group(1)
    else:
        return f'chat-{idx}'

def extract_chats():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    files = [f for f in os.listdir(CHATS_DIR) if f.lower().endswith('.zip')]
    if not files:
        st.warning('No se encontraron archivos .zip en la carpeta chats/.')
        return
    for idx, fname in enumerate(files):
        chat_name = get_chat_name(fname, idx)
        chat_out_dir = os.path.join(OUTPUT_DIR, chat_name)
        os.makedirs(chat_out_dir, exist_ok=True)
        with zipfile.ZipFile(os.path.join(CHATS_DIR, fname), 'r') as zip_ref:
            zip_ref.extractall(chat_out_dir)
        st.info(f'Extraído {fname} a {chat_out_dir}')
DATE_FORMATS = [
    '%d/%m/%Y, %H:%M',  # WhatsApp export format
    '%d/%m/%y, %H:%M',  # Sometimes year is 2 digits
]

# Helper to parse WhatsApp txt lines
LINE_PATTERN = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{2}:\d{2}) - (.*?): (.*)$')

def parse_date(date_str):
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def list_chats():
    return [d for d in os.listdir(OUTPUT_DIR) if os.path.isdir(os.path.join(OUTPUT_DIR, d))]

def get_txt_file(chat_dir):
    txts = glob.glob(os.path.join(OUTPUT_DIR, chat_dir, '*.txt'))
    return txts[0] if txts else None

def parse_messages(txt_file, start_date=None, end_date=None):
    messages = []
    with open(txt_file, encoding='utf-8') as f:
        for line in f:
            m = LINE_PATTERN.match(line)
            if m:
                date = parse_date(m.group(1))
                if date and ((not start_date or date >= start_date) and (not end_date or date <= end_date)):
                    messages.append({'date': date, 'user': m.group(2), 'text': m.group(3)})
    return messages


# Relacionar media con mensajes para filtrar por fecha
def list_media_by_date(chat_dir, txt_file, start_date=None, end_date=None):
    media_dir = os.path.join(OUTPUT_DIR, chat_dir)
    if not os.path.exists(media_dir):
        return []
    # Buscar nombres de archivos multimedia referenciados en los mensajes dentro del rango de fechas
    media_files = set()
    with open(txt_file, encoding='utf-8') as f:
        for line in f:
            m = LINE_PATTERN.match(line)
            if m:
                date = parse_date(m.group(1))
                if date and ((not start_date or date >= start_date) and (not end_date or date <= end_date)):
                    # Buscar referencias a archivos (ej: "IMG-2023...jpg (archivo adjunto)")
                    # WhatsApp suele poner el nombre del archivo en el texto
                    file_refs = re.findall(r'(\S+\.(jpg|jpeg|png|mp4|mp3|ogg|wav|opus|pdf|docx|xlsx|gif|webp|mov|avi|m4a|aac|heic|heif|3gp|zip|rar))', m.group(3), re.IGNORECASE)
                    for ref in file_refs:
                        media_files.add(ref[0])
    # Solo mostrar los archivos que existen en la carpeta y están referenciados en el rango de fechas
    files = [f for f in os.listdir(media_dir) if f in media_files]
    return files

st.title('WhatsApp Viewer')


# Botón para extraer los chats
if st.button('Extraer chats de los archivos .zip en la carpeta chats/'):
    extract_chats()
    st.success('Extracción completada. Recarga la página si no ves los nuevos chats.')

chats = list_chats()
if not chats:
    st.warning('No se encontraron chats. Ejecuta la extracción primero.')
    st.stop()

chat = st.selectbox('Selecciona el chat', chats)
txt_file = get_txt_file(chat)



if txt_file:
    st.subheader('Filtros y visualización de búsqueda')
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input('Fecha de inicio', value=None)
    with col2:
        end = st.date_input('Fecha de fin', value=None)
    start_dt = datetime.combine(start, datetime.min.time()) if start else None
    end_dt = datetime.combine(end, datetime.max.time()) if end else None

    search_text = st.text_input('Buscar texto en mensajes', value='')
    col3, col4 = st.columns(2)
    with col3:
        case_sensitive = st.checkbox('Distinguir mayúsculas/minúsculas', value=False)
    with col4:
        whole_word = st.checkbox('Coincidencia exacta de palabra', value=False)

    col5, col6 = st.columns(2)
    with col5:
        show_user = st.checkbox('Mostrar remitente del mensaje', value=True)
    with col6:
        show_date = st.checkbox('Mostrar fecha del mensaje', value=True)


    # Dropdown para elegir el orden de los mensajes
    order = st.selectbox('Orden de los mensajes', ['Ascendente (más antiguos primero)', 'Descendente (más recientes primero)'], index=0)
    messages = parse_messages(txt_file, start_dt, end_dt)
    if order == 'Descendente (más recientes primero)':
        messages = list(reversed(messages))

    # Filtrado por texto
    def message_matches(msg_text, search_text, case_sensitive, whole_word):
        if not search_text:
            return True
        flags = 0 if case_sensitive else re.IGNORECASE
        if whole_word:
            # Buscar cada palabra por separado
            words = search_text.split()
            return all(re.search(rf'\\b{re.escape(word)}\\b', msg_text, flags) for word in words)
        else:
            return search_text in msg_text if case_sensitive else search_text.lower() in msg_text.lower()

    filtered_messages = [msg for msg in messages if message_matches(msg['text'], search_text, case_sensitive, whole_word)]

    st.subheader('Mensajes')
    import mimetypes
    MEDIA_EXTS = (
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'heic', 'heif',
        'mp4', 'mov', 'avi', 'm4v', 'webm',
        'mp3', 'ogg', 'wav', 'opus', 'm4a', 'aac'
    )
    last_day = None
    for msg in filtered_messages:
        msg_day = msg['date'].date()
        if last_day != msg_day:
            # Día de la semana en español
            dias_semana = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            dia_semana = dias_semana[msg["date"].weekday()]
            st.markdown(f'<div style="background:#222;padding:6px 0 6px 0;text-align:center;border-radius:8px;margin:16px 0 8px 0;font-weight:bold;letter-spacing:1px;">{dia_semana.capitalize()}, {msg["date"].strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)
            last_day = msg_day
        parts = []
        if show_date:
            parts.append(f"[{msg['date'].strftime('%d/%m/%Y %H:%M')}] ")
        if show_user:
            parts.append(f"{msg['user']}: ")
        parts.append(msg['text'])
        st.write(''.join(parts))

        # Buscar referencias a archivos multimedia en el texto del mensaje, incluyendo casos con carácter invisible y ' (archivo adjunto)'
        file_refs = re.findall(r'[\u200e]?([\w\-]+\.(?:' + '|'.join(MEDIA_EXTS) + '))(?: \(archivo adjunto\))?', msg['text'], re.IGNORECASE)
        for media_file in file_refs:
            # Limpiar posibles caracteres invisibles y sufijos
            clean_file = media_file.replace('\u200e', '').replace(' (archivo adjunto)', '').strip()
            file_path = os.path.join(OUTPUT_DIR, str(chat), clean_file)
            if not os.path.exists(file_path):
                file_path = os.path.join(OUTPUT_DIR, str(chat), os.path.basename(clean_file))
            if os.path.exists(file_path):
                mime, _ = mimetypes.guess_type(file_path)
                if mime:
                    if mime.startswith('image'):
                        with open(file_path, 'rb') as img:
                            st.image(img.read(), use_container_width=True)
                    elif mime.startswith('video'):
                        with open(file_path, 'rb') as vid:
                            st.video(vid.read())
                    elif mime.startswith('audio'):
                        with open(file_path, 'rb') as aud:
                            st.audio(aud.read())
                else:
                    st.markdown(f"[Descargar {clean_file}](file://{os.path.abspath(file_path)})")
else:
    st.warning('No .txt file found in this chat.')
