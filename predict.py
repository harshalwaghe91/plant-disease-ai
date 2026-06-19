# predict.py
"""
Standalone prediction module.
Usage: python predict.py --image path/to/image.jpg
"""
import os
import sys
import argparse
import numpy as np

def load_model(model_path='model/model.h5'):
    """Load the trained Keras model."""
    try:
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)
        print(f"[INFO] Model loaded from {model_path}")
        return model
    except Exception as e:
        print(f"[ERROR] Could not load model: {e}")
        return None

def predict_disease(image_path, model, class_names):
    """Run prediction on a single image."""
    from utils import preprocess_image, format_confidence, get_confidence_level
    from disease_data import get_disease_info

    img_array = preprocess_image(image_path)
    predictions = model.predict(img_array, verbose=0)[0]
    top_idx = int(np.argmax(predictions))
    confidence = float(predictions[top_idx])

    class_name = class_names[top_idx]
    disease_info = get_disease_info(class_name)
    conf_label, conf_color = get_confidence_level(confidence)

    # Top 3 predictions
    top3_idx = np.argsort(predictions)[::-1][:3]
    top3 = [
        {"class": class_names[i], "confidence": float(predictions[i])}
        for i in top3_idx
    ]

    return {
        "class_name": class_name,
        "confidence": confidence,
        "confidence_pct": format_confidence(confidence),
        "confidence_label": conf_label,
        "disease_info": disease_info,
        "top3": top3
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plant Disease Predictor")
    parser.add_argument("--image", required=True, help="Path to leaf image")
    parser.add_argument("--model", default="model/model.h5", help="Path to model.h5")
    args = parser.parse_args()

    from disease_data import CLASS_NAMES
    model = load_model(args.model)
    if model is None:
        sys.exit(1)

    result = predict_disease(args.image, model, CLASS_NAMES)
    print("\n" + "="*50)
    print(f"Disease Detected : {result['disease_info']['display_name']}")
    print(f"Confidence       : {result['confidence_pct']} ({result['confidence_label']})")
    print(f"Plant            : {result['disease_info']['plant']}")
    print(f"Severity         : {result['disease_info']['severity']}")
    print("\nTop 3 Predictions:")
    for i, p in enumerate(result['top3'], 1):
        print(f"  {i}. {p['class']:30s} {p['confidence']*100:.1f}%")
    print("="*50)
