# backend/helpers.py
import os
import qrcode
from io import BytesIO
import base64
from werkzeug.utils import secure_filename
from datetime import datetime
from config import Config

def allowed_file(filename):
    """
    Verifica se a extensão do arquivo é permitida.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def save_file(file):
    """
    Salva o arquivo com nome único no diretório de uploads.
    Retorna o nome do arquivo ou None se falhar.
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        file.save(os.path.join(Config.UPLOAD_FOLDER, unique_filename))
        return unique_filename
    return None

def gerar_qr_code(data):
    """
    Gera um QR Code para os dados fornecidos.
    Retorna uma string base64 da imagem.
    """
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str