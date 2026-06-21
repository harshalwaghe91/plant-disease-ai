# app.py
"""
AI-Powered Plant Disease Detection System
Flask Web Application
"""

import os
import json
import uuid
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, jsonify, send_file)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from disease_data import DISEASE_DATABASE, CLASS_NAMES, get_disease_info, get_all_diseases
from utils import (allowed_file, preprocess_image, format_confidence,
                   get_confidence_level, save_prediction_to_history, load_history)

# ─── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'plant-disease-detection-secret-2024')

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
MODEL_PATH    = os.path.join(BASE_DIR, 'model', 'model.h5')
HISTORY_FILE  = os.path.join(BASE_DIR, 'predictions_history.json')
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Admin Credentials (change in production!) ────────────────────────────────
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD_HASH = generate_password_hash(
    os.environ.get('ADMIN_PASSWORD', 'admin123')
)

# ─── Model Loading ────────────────────────────────────────────────────────────
# ─── Auto Download Model ──────────────────────────────────────────────────────
def download_model_if_missing():
    """Download model.h5 from Google Drive if not present."""
    if os.path.exists(MODEL_PATH):
        print("[INFO] model.h5 already exists, skipping download.")
        return

    print("[INFO] model.h5 not found. Downloading from Google Drive...")
    try:
        import subprocess
        # Install gdown if not available
        subprocess.run(
            ["pip", "install", "gdown", "--quiet"],
            check=True
        )
        import gdown
        file_id = "1euqkE-twT67cfOWWWdLkQoTZeXXQ6isF"
        url = f"https://drive.google.com/uc?id={file_id}"
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        gdown.download(url, MODEL_PATH, quiet=False)
        print("[INFO] Model downloaded successfully!")
    except Exception as e:
        print(f"[ERROR] Could not download model: {e}")
model = None

def load_model():
    global model
    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] model.h5 not found. Running in demo mode.")
        return False
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"[INFO] Model loaded: {MODEL_PATH}")
        class_names_path = os.path.join(BASE_DIR, 'model', 'class_names.json')
        if os.path.exists(class_names_path):
            with open(class_names_path) as f:
                saved_classes = json.load(f)
            CLASS_NAMES.clear()
            CLASS_NAMES.extend(saved_classes)
        return True
    except ImportError:
        print("[WARNING] TensorFlow not installed. Running in demo mode.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

# ─── Auth Decorator ───────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ─── User Routes ──────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', num_diseases=len(DISEASE_DATABASE))

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(url_for('index'))

    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload JPG, PNG, or WEBP.', 'danger')
        return redirect(url_for('index'))

    # Save uploaded file
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file.save(filepath)

    if model is None:
        # Demo mode: return a mock result when model is not trained yet
        flash('Model not loaded. Showing demo result.', 'warning')
        disease_info = get_disease_info("Tomato_Early_Blight")
        result = {
            "class_name": "Tomato_Early_Blight",
            "confidence": 0.923,
            "confidence_pct": "92.3%",
            "confidence_label": "Very High",
            "confidence_color": "#28a745",
            "disease_info": disease_info,
            "image_url": url_for('static', filename=f'uploads/{unique_name}'),
            "top3": [
                {"class": "Tomato_Early_Blight", "display": "Tomato Early Blight", "confidence": 92.3},
                {"class": "Tomato_Late_Blight",  "display": "Tomato Late Blight",  "confidence": 4.1},
                {"class": "Healthy",             "display": "Healthy",              "confidence": 3.6},
            ],
            "demo_mode": True
        }
        save_prediction_to_history(
            HISTORY_FILE, unique_name,
            result["class_name"], result["confidence"],
            disease_info.get("plant", "Unknown")
        )
        return render_template('result.html', result=result)

    try:
        import numpy as np
        img_array = preprocess_image(filepath)
        preds = model.predict(img_array, verbose=0)[0]
        top_idx = int(np.argmax(preds))
        confidence = float(preds[top_idx])
        class_name = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else "Unknown"
        disease_info = get_disease_info(class_name)
        conf_label, conf_color = get_confidence_level(confidence)

        top3_idx = np.argsort(preds)[::-1][:3]
        top3 = []
        for i in top3_idx:
            cn = CLASS_NAMES[i] if i < len(CLASS_NAMES) else f"Class_{i}"
            di = get_disease_info(cn)
            top3.append({
                "class": cn,
                "display": di.get("display_name", cn.replace("_", " ")),
                "confidence": round(float(preds[i]) * 100, 1)
            })

        result = {
            "class_name": class_name,
            "confidence": confidence,
            "confidence_pct": format_confidence(confidence),
            "confidence_label": conf_label,
            "confidence_color": conf_color,
            "disease_info": disease_info,
            "image_url": url_for('static', filename=f'uploads/{unique_name}'),
            "top3": top3,
            "demo_mode": False
        }

        save_prediction_to_history(
            HISTORY_FILE, unique_name, class_name, confidence,
            disease_info.get("plant", "Unknown")
        )
        return render_template('result.html', result=result)

    except Exception as e:
        flash(f'Prediction error: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/diseases')
def diseases():
    """Public disease library page."""
    return render_template('diseases.html', diseases=DISEASE_DATABASE)

# ─── Admin Routes ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if (username == ADMIN_USERNAME and
                check_password_hash(ADMIN_PASSWORD_HASH, password)):
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('Welcome back, Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    history = load_history(HISTORY_FILE)
    stats = {
        "total_predictions": len(history),
        "num_diseases": len(DISEASE_DATABASE),
        "recent": history[:10]
    }
    # Disease frequency
    freq = {}
    for h in history:
        freq[h['disease']] = freq.get(h['disease'], 0) + 1
    top_diseases = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]
    stats['top_diseases'] = [{"name": k.replace("_"," "), "count": v}
                              for k, v in top_diseases]
    return render_template('admin.html', stats=stats, diseases=DISEASE_DATABASE)

@app.route('/admin/history')
@admin_required
def admin_history():
    history = load_history(HISTORY_FILE)
    return render_template('history.html', history=history)

@app.route('/admin/add_disease', methods=['POST'])
@admin_required
def add_disease():
    """Add a new disease entry to the in-memory database."""
    data = request.json or {}
    key = data.get('key', '').strip().replace(' ', '_')
    if not key:
        return jsonify({"success": False, "error": "Key is required"}), 400
    if key in DISEASE_DATABASE:
        return jsonify({"success": False, "error": "Disease already exists"}), 409

    DISEASE_DATABASE[key] = {
        "display_name": data.get("display_name", key.replace("_", " ")),
        "plant":        data.get("plant", "Unknown"),
        "description":  data.get("description", ""),
        "symptoms":     data.get("symptoms", []),
        "causes":       data.get("causes", []),
        "severity":     data.get("severity", "Unknown"),
        "chemical_treatment": data.get("chemical_treatment", ""),
        "organic_treatment":  data.get("organic_treatment", ""),
        "prevention":   data.get("prevention", []),
        "color":        data.get("color", "#6c757d")
    }
    if key not in CLASS_NAMES:
        CLASS_NAMES.append(key)
    return jsonify({"success": True, "message": f"Disease '{key}' added."})

@app.route('/admin/delete_prediction/<pred_id>', methods=['POST'])
@admin_required
def delete_prediction(pred_id):
    history = load_history(HISTORY_FILE)
    history = [h for h in history if h.get('id') != pred_id]
    import json
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    return jsonify({"success": True})

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.route('/api/diseases')
def api_diseases():
    return jsonify(list(DISEASE_DATABASE.keys()))

@app.route('/api/disease/<name>')
def api_disease_info(name):
    info = get_disease_info(name)
    return jsonify(info)

@app.route('/api/stats')
def api_stats():
    history = load_history(HISTORY_FILE)
    return jsonify({
        "total": len(history),
        "diseases": len(DISEASE_DATABASE),
        "model_loaded": model is not None
    })

# ─── PDF Report ───────────────────────────────────────────────────────────────
@app.route('/download_report', methods=['POST'])
def download_report():
    """Generate and download PDF report of prediction."""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        import io

        data = request.json
        disease_name = data.get('disease_name', 'Unknown')
        confidence   = data.get('confidence', 'N/A')
        plant        = data.get('plant', 'Unknown')
        severity     = data.get('severity', 'Unknown')
        symptoms     = data.get('symptoms', [])
        chemical     = data.get('chemical_treatment', '')
        organic      = data.get('organic_treatment', '')
        prevention   = data.get('prevention', [])
        description  = data.get('description', '')

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        W, H = A4

        # Header
        c.setFillColor(colors.HexColor('#2d6a4f'))
        c.rect(0, H - 80, W, 80, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(2*cm, H - 45, "Plant Disease Detection Report")
        c.setFont("Helvetica", 11)
        c.drawString(2*cm, H - 65, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        # Disease info box
        y = H - 110
        c.setFillColor(colors.HexColor('#f8f9fa'))
        c.rect(1.5*cm, y - 80, W - 3*cm, 75, fill=1, stroke=0)
        c.setFillColor(colors.HexColor('#2d6a4f'))
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, y - 20, f"Disease: {disease_name}")
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, y - 40, f"Plant: {plant}")
        c.drawString(2*cm, y - 58, f"Confidence: {confidence}")
        c.drawString(10*cm, y - 40, f"Severity: {severity}")

        def section(title, content_lines, start_y):
            c.setFillColor(colors.HexColor('#2d6a4f'))
            c.setFont("Helvetica-Bold", 13)
            c.drawString(2*cm, start_y, title)
            c.setFillColor(colors.black)
            c.setFont("Helvetica", 11)
            cur_y = start_y - 16
            for line in content_lines:
                if cur_y < 3*cm:
                    c.showPage()
                    cur_y = H - 3*cm
                wrapped = [line[i:i+95] for i in range(0, len(line), 95)]
                for w in wrapped:
                    c.drawString(2.5*cm, cur_y, f"• {w}")
                    cur_y -= 14
            return cur_y - 10

        cur_y = y - 110
        cur_y = section("Description", [description], cur_y)
        cur_y = section("Symptoms", symptoms, cur_y)
        cur_y = section("Chemical Treatment", [chemical], cur_y)
        cur_y = section("Organic Treatment", [organic], cur_y)
        cur_y = section("Prevention Methods", prevention, cur_y)

        # Footer
        c.setFillColor(colors.HexColor('#6c757d'))
        c.setFont("Helvetica", 9)
        c.drawString(2*cm, 1.5*cm, "AI Plant Disease Detection System | For informational purposes only. Consult an agronomist for confirmation.")

        c.save()
        buffer.seek(0)
        filename = f"plant_disease_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(buffer, mimetype='application/pdf',
                         as_attachment=True, download_name=filename)

    except ImportError:
        return jsonify({"error": "reportlab not installed. Run: pip install reportlab"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Error Handlers ───────────────────────────────────────────────────────────
@app.errorhandler(413)
def file_too_large(e):
    flash('File too large. Maximum size is 10MB.', 'danger')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    download_model_if_missing()
    load_model()
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    port  = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug)
else:
    # Production: download and load model at startup
    download_model_if_missing()
    load_model()
