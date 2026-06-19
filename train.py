# train.py
"""
Training Script for Plant Disease Detection
Uses MobileNetV2 Transfer Learning on PlantVillage Dataset

Dataset structure expected:
dataset/
  train/
    Healthy/
    Tomato_Early_Blight/
    ... (one folder per class)
  val/
    Healthy/
    ...

Usage:
  python train.py --data_dir dataset --epochs 30 --batch_size 32
"""

import os
import sys
import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import json
from datetime import datetime

# ─── Argument Parser ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train Plant Disease Detection Model")
parser.add_argument("--data_dir",   default="dataset",    help="Root dataset directory")
parser.add_argument("--model_dir",  default="model",      help="Directory to save model")
parser.add_argument("--epochs",     type=int, default=30, help="Max training epochs")
parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
parser.add_argument("--img_size",   type=int, default=224,help="Image size (square)")
parser.add_argument("--lr",         type=float,default=1e-4,help="Initial learning rate")
args = parser.parse_args()

# ─── Imports ──────────────────────────────────────────────────────────────────
print("[INFO] Loading TensorFlow...")
import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers, callbacks
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

print(f"[INFO] TensorFlow version: {tf.__version__}")
gpus = tf.config.list_physical_devices('GPU')
print(f"[INFO] GPUs available: {len(gpus)}")

# ─── Constants ────────────────────────────────────────────────────────────────
IMG_SIZE    = (args.img_size, args.img_size)
BATCH_SIZE  = args.batch_size
EPOCHS      = args.epochs
LR          = args.lr
DATA_DIR    = args.data_dir
MODEL_DIR   = args.model_dir
TRAIN_DIR   = os.path.join(DATA_DIR, "train")
VAL_DIR     = os.path.join(DATA_DIR, "val")
os.makedirs(MODEL_DIR, exist_ok=True)

# ─── Data Generators ──────────────────────────────────────────────────────────
print("\n[INFO] Setting up data generators with augmentation...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=40,
    width_shift_range=0.25,
    height_shift_range=0.25,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    vertical_flip=False,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(rescale=1./255)

train_gen = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=True
)

val_gen = val_datagen.flow_from_directory(
    VAL_DIR,
    target_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

NUM_CLASSES = train_gen.num_classes
CLASS_NAMES = list(train_gen.class_indices.keys())
print(f"[INFO] Classes ({NUM_CLASSES}): {CLASS_NAMES}")

# Save class names for inference
with open(os.path.join(MODEL_DIR, "class_names.json"), "w") as f:
    json.dump(CLASS_NAMES, f)
print(f"[INFO] Class names saved to {MODEL_DIR}/class_names.json")

# ─── Model Architecture ───────────────────────────────────────────────────────
print("\n[INFO] Building MobileNetV2 Transfer Learning model...")

base_model = MobileNetV2(
    input_shape=(*IMG_SIZE, 3),
    include_top=False,
    weights='imagenet'
)
base_model.trainable = False  # Freeze base initially

inputs = tf.keras.Input(shape=(*IMG_SIZE, 3))
x = base_model(inputs, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.BatchNormalization()(x)
x = layers.Dense(512, activation='relu')(x)
x = layers.Dropout(0.4)(x)
x = layers.Dense(256, activation='relu')(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(NUM_CLASSES, activation='softmax')(x)

model = Model(inputs, outputs)
model.summary()

# ─── Phase 1: Train Head Only ─────────────────────────────────────────────────
print("\n[INFO] Phase 1: Training classification head...")

model.compile(
    optimizer=optimizers.Adam(learning_rate=LR),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

cb_list_phase1 = [
    callbacks.EarlyStopping(monitor='val_accuracy', patience=5,
                            restore_best_weights=True, verbose=1),
    callbacks.ModelCheckpoint(
        os.path.join(MODEL_DIR, "best_phase1.h5"),
        monitor='val_accuracy', save_best_only=True, verbose=1
    ),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                                patience=3, min_lr=1e-7, verbose=1)
]

phase1_epochs = min(15, EPOCHS // 2)
history1 = model.fit(
    train_gen,
    epochs=phase1_epochs,
    validation_data=val_gen,
    callbacks=cb_list_phase1,
    verbose=1
)

# ─── Phase 2: Fine-tuning ─────────────────────────────────────────────────────
print("\n[INFO] Phase 2: Fine-tuning top layers of MobileNetV2...")

# Unfreeze last 30 layers of base model
base_model.trainable = True
for layer in base_model.layers[:-30]:
    layer.trainable = False

model.compile(
    optimizer=optimizers.Adam(learning_rate=LR / 10),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

cb_list_phase2 = [
    callbacks.EarlyStopping(monitor='val_accuracy', patience=7,
                            restore_best_weights=True, verbose=1),
    callbacks.ModelCheckpoint(
        os.path.join(MODEL_DIR, "model.h5"),
        monitor='val_accuracy', save_best_only=True, verbose=1
    ),
    callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.3,
                                patience=4, min_lr=1e-8, verbose=1),
    callbacks.CSVLogger(os.path.join(MODEL_DIR, "training_log.csv"))
]

history2 = model.fit(
    train_gen,
    epochs=EPOCHS,
    initial_epoch=len(history1.history['loss']),
    validation_data=val_gen,
    callbacks=cb_list_phase2,
    verbose=1
)

# ─── Merge Histories ──────────────────────────────────────────────────────────
def merge_history(h1, h2):
    merged = {}
    for k in h1.history:
        merged[k] = h1.history[k] + h2.history[k]
    return merged

full_history = merge_history(history1, history2)

# ─── Plots ────────────────────────────────────────────────────────────────────
print("\n[INFO] Generating training plots...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Accuracy
ax1.plot(full_history['accuracy'], label='Train Accuracy', color='#2196F3', linewidth=2)
ax1.plot(full_history['val_accuracy'], label='Val Accuracy', color='#4CAF50', linewidth=2)
ax1.set_title('Model Accuracy', fontsize=14, fontweight='bold')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0.95, color='red', linestyle='--', alpha=0.5, label='95% target')

# Loss
ax2.plot(full_history['loss'], label='Train Loss', color='#FF5722', linewidth=2)
ax2.plot(full_history['val_loss'], label='Val Loss', color='#9C27B0', linewidth=2)
ax2.set_title('Model Loss', fontsize=14, fontweight='bold')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(MODEL_DIR, 'training_curves.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"[INFO] Training curves saved.")

# ─── Evaluation & Confusion Matrix ───────────────────────────────────────────
print("\n[INFO] Evaluating model on validation set...")
val_gen.reset()
val_loss, val_acc = model.evaluate(val_gen, verbose=1)
print(f"\n[RESULT] Validation Accuracy: {val_acc*100:.2f}%")
print(f"[RESULT] Validation Loss:     {val_loss:.4f}")

print("\n[INFO] Generating confusion matrix...")
val_gen.reset()
y_pred_probs = model.predict(val_gen, verbose=1)
y_pred = np.argmax(y_pred_probs, axis=1)
y_true = val_gen.classes

print("\nClassification Report:")
print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(
    cm, annot=True, fmt='d', cmap='Blues',
    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES
)
plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(MODEL_DIR, 'confusion_matrix.png'), dpi=150, bbox_inches='tight')
plt.close()
print(f"[INFO] Confusion matrix saved.")

# ─── Save Final Model ─────────────────────────────────────────────────────────
final_path = os.path.join(MODEL_DIR, 'model.h5')
model.save(final_path)
print(f"\n[SUCCESS] Model saved to: {final_path}")

# Save training summary
summary = {
    "timestamp": datetime.now().isoformat(),
    "num_classes": NUM_CLASSES,
    "class_names": CLASS_NAMES,
    "img_size": args.img_size,
    "batch_size": BATCH_SIZE,
    "final_val_accuracy": round(val_acc * 100, 2),
    "final_val_loss": round(val_loss, 4),
    "total_epochs": len(full_history['loss'])
}
with open(os.path.join(MODEL_DIR, "training_summary.json"), "w") as f:
    json.dump(summary, f, indent=2)

print(f"\n{'='*60}")
print(f"TRAINING COMPLETE")
print(f"  Validation Accuracy : {val_acc*100:.2f}%")
print(f"  Model saved at      : {final_path}")
print(f"{'='*60}")
