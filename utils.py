# utils.py
import os
import numpy as np
from PIL import Image
import io
import base64
from datetime import datetime

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
IMG_SIZE = (224, 224)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(image_path):
    """Load and preprocess image for model prediction."""
    img = Image.open(image_path).convert('RGB')
    img = img.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def preprocess_image_bytes(image_bytes):
    """Preprocess image from bytes object."""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize(IMG_SIZE)
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def image_to_base64(image_path):
    """Convert image to base64 for embedding in HTML."""
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    ext = image_path.rsplit('.', 1)[1].lower()
    mime = 'jpeg' if ext == 'jpg' else ext
    return f"data:image/{mime};base64,{encoded}"

def format_confidence(confidence):
    """Format confidence as percentage string."""
    return f"{confidence * 100:.1f}%"

def get_confidence_level(confidence):
    """Return confidence level label and color."""
    if confidence >= 0.90:
        return "Very High", "#28a745"
    elif confidence >= 0.75:
        return "High", "#20c997"
    elif confidence >= 0.55:
        return "Moderate", "#fd7e14"
    else:
        return "Low", "#dc3545"

def save_prediction_to_history(db_path, filename, disease_name, confidence, plant):
    """Append prediction to history JSON file."""
    import json
    record = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "disease": disease_name,
        "plant": plant,
        "confidence": round(confidence * 100, 1)
    }
    history = []
    if os.path.exists(db_path):
        with open(db_path, 'r') as f:
            try:
                history = json.load(f)
            except Exception:
                history = []
    history.insert(0, record)
    history = history[:500]  # Keep last 500 records
    with open(db_path, 'w') as f:
        json.dump(history, f, indent=2)
    return record

def load_history(db_path):
    """Load prediction history."""
    import json
    if not os.path.exists(db_path):
        return []
    with open(db_path, 'r') as f:
        try:
            return json.load(f)
        except Exception:
            return []
