import os
import cv2
import shutil
import random
import numpy as np
from pathlib import Path

# --- CONFIGURAȚII ---
BASE_DIR = Path(".")  # Directorul curent (root-ul proiectului)
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Folderele de destinație pentru split
TRAIN_DIR = BASE_DIR / "data" / "train"
VAL_DIR = BASE_DIR / "data" / "validation"
TEST_DIR = BASE_DIR / "data" / "test"

IMG_SIZE = (128, 128)  # Dimensiunea țintă (width, height)
SPLIT_RATIOS = (0.70, 0.15, 0.15)  # Train, Validation, Test

# Extensiile acceptate
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}

def clean_and_create_dirs():
    """Creează structura de directoare. Dacă există, șterge conținutul vechi pentru a nu duplica."""
    dirs_to_create = [PROCESSED_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR]
    
    for d in dirs_to_create:
        if d.exists():
            shutil.rmtree(d) # Curățăm folderul dacă există deja
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Folder creat/resetat: {d}")

def process_image(img_path):
    """
    Citește imaginea, o face Grayscale și o redimensionează.
    Returnează imaginea procesată.
    """
    # 1. Citire imagine
    img = cv2.imread(str(img_path))
    if img is None:
        return None
    
    # 2. Conversie Grayscale (dacă nu e deja)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Resize la 128x128
    img_resized = cv2.resize(img_gray, IMG_SIZE, interpolation=cv2.INTER_AREA)
    
    return img_resized

def save_image(img, dest_dir, filename):
    """Salvează imaginea în folderul specificat."""
    save_path = dest_dir / filename
    cv2.imwrite(str(save_path), img)

def main():
    print("🚀 Începere procesare date...")
    clean_and_create_dirs()

    # Identificăm clasele pe baza folderelor din RAW (ex: usa_stanga, capota, etc.)
    classes = [d.name for d in RAW_DIR.iterdir() if d.is_dir()]
    
    print(f"📦 Clase detectate: {classes}")

    total_images = 0

    for class_name in classes:
        print(f"\nProcesare clasă: {class_name}...")
        
        # Căile sursă
        class_raw_dir = RAW_DIR / class_name
        
        # Creăm subfolderele pentru clasa curentă în destinații
        (PROCESSED_DIR / class_name).mkdir(exist_ok=True)
        (TRAIN_DIR / class_name).mkdir(exist_ok=True)
        (VAL_DIR / class_name).mkdir(exist_ok=True)
        (TEST_DIR / class_name).mkdir(exist_ok=True)

        # Colectăm toate imaginile valide
        images = [f for f in class_raw_dir.iterdir() if f.suffix.lower() in VALID_EXTENSIONS]
        
        # Amestecăm imaginile (Shuffle) pentru randomizare
        random.shuffle(images)
        
        n_total = len(images)
        n_train = int(n_total * SPLIT_RATIOS[0])
        n_val = int(n_total * SPLIT_RATIOS[1])
        # Restul merge la test (pentru a acoperi rotunjirile)
        
        for i, img_file in enumerate(images):
            # Procesare
            processed_img = process_image(img_file)
            
            if processed_img is None:
                print(f"⚠️ Imagine coruptă sau ilizibilă: {img_file}")
                continue

            # Determinare set (Train / Val / Test)
            if i < n_train:
                dest_folder = TRAIN_DIR / class_name
            elif i < n_train + n_val:
                dest_folder = VAL_DIR / class_name
            else:
                dest_folder = TEST_DIR / class_name

            # Salvare
            # 1. Salvăm o copie în 'processed' (opțional, conform README-ului tău)
            save_image(processed_img, PROCESSED_DIR / class_name, img_file.name)
            
            # 2. Salvăm în setul specific (Train/Val/Test)
            save_image(processed_img, dest_folder, img_file.name)
            
        total_images += n_total
        print(f"   -> {n_total} imagini procesate (Train: {n_train}, Val: {n_val}, Test: {n_total - n_train - n_val})")

    print("\n" + "="*50)
    print(f"✅ Procesare completă! Total imagini procesate: {total_images}")
    print(f"📁 Verifică folderele: data/train, data/validation, data/test")

if __name__ == "__main__":
    main()