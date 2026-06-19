import os
import shutil
import random

# Exact folder names confirmed from your PlantVillage directory
FOLDER_MAP = {
    'Pepper__bell___healthy':           'Pepper_Healthy',
    'Pepper__bell___Bacterial_spot':    'Pepper_Bacterial_Spot',
    'Potato___Early_blight':            'Potato_Early_Blight',
    'Potato___healthy':                 'Healthy',
    'Potato___Late_blight':             'Potato_Late_Blight',
    'Tomato_Early_blight':              'Tomato_Early_Blight',
    'Tomato_healthy':                   'Healthy',
    'Tomato_Late_blight':               'Tomato_Late_Blight',
    'Tomato_Leaf_Mold':                 'Tomato_Leaf_Mold',
}

SRC = 'raw_dataset/PlantVillage'

if not os.path.exists(SRC):
    print(f"ERROR: '{SRC}' folder not found.")
    exit()

# First delete any partial dataset from the previous failed run
if os.path.exists('dataset'):
    print("Removing previous partial dataset folder...")
    shutil.rmtree('dataset')
    print("Removed. Starting fresh.\n")

random.seed(42)
total_copied = 0
total_skipped = 0

for kaggle_name, our_name in FOLDER_MAP.items():
    src_path = os.path.join(SRC, kaggle_name)

    if not os.path.exists(src_path):
        print(f"NOT FOUND: {kaggle_name}")
        continue

    imgs = [
        f for f in os.listdir(src_path)
        if f.lower().endswith(('.jpg', '.jpeg', '.png'))
    ]
    random.shuffle(imgs)
    split = int(len(imgs) * 0.8)

    copied = 0
    for split_name, files in [('train', imgs[:split]), ('val', imgs[split:])]:
        dest = os.path.join('dataset', split_name, our_name)
        os.makedirs(dest, exist_ok=True)
        for f in files:
            try:
                shutil.copy(
                    os.path.join(src_path, f),
                    os.path.join(dest, f)
                )
                copied += 1
            except Exception as e:
                print(f"  SKIP: {f} ({e})")
                total_skipped += 1

    total_copied += copied
    print(f"OK  {our_name:30s} | train: {split:4d}  val: {len(imgs)-split:3d}  total: {len(imgs):4d}")

print(f"\n{'='*60}")
print(f"DONE!")
print(f"Total images copied : {total_copied}")
print(f"Total files skipped : {total_skipped}")
print(f"Dataset saved in    : dataset/train/ and dataset/val/")
print(f"{'='*60}")