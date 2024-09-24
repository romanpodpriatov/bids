# utils.py
import uuid
import os
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

def generate_uuid():
    return str(uuid.uuid4())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def save_image(file, upload_folder):
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filename

def calculate_end_time(duration_hours):
    return datetime.utcnow() + timedelta(hours=duration_hours)
