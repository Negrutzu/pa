#!/usr/bin/env python3
"""
generate_dataset_from_contours.py
Preia PNG-urile din assets/base_contours/ și generează dataset realist.
Salvează în: data/raw/<clasa>/
"""
import os, random, math
import numpy as np
import cv2
from PIL import Image, ImageEnhance

BASE_DIR = "assets/base_contours"
OUT_DIR = "data/raw"
IMG_SIZE = 384
PER_CLASS = 200  # images per class (ajustează dacă vrei mai multe)

os.makedirs(OUT_DIR, exist_ok=True)

def load_base(name):
    path = os.path.join(BASE_DIR, f"{name}.png")
    im = Image.open(path).convert("RGBA")
    return im

def rgba_to_cv(img_pil):
    arr = np.array(img_pil)  # H W 4
    # separate alpha mask and rgb
    alpha = arr[:,:,3] / 255.0
    rgb = arr[:,:,:3].astype(np.uint8)
    return rgb, (alpha*255).astype(np.uint8)

def random_scale_rotate(img, alpha):
    # img: cv RGB, alpha: single channel
    h,w = img.shape[:2]
    # random scale 0.85 - 1.05
    s = random.uniform(0.85, 1.05)
    angle = random.uniform(-8, 8)
    M = cv2.getRotationMatrix2D((w/2,h/2), angle, s)
    img_t = cv2.warpAffine(img, M, (w,h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    alpha_t = cv2.warpAffine(alpha, M, (w,h), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return img_t, alpha_t

def apply_perspective(img, alpha, max_shift=30):
    h,w = img.shape[:2]
    pts1 = np.float32([[0,0],[w,0],[w,h],[0,h]])
    shift = lambda: random.randint(-max_shift, max_shift)
    pts2 = np.float32([
        [max(0, 0 + shift()), max(0, 0 + shift())],
        [min(w-1, w + shift()), max(0, 0 + shift())],
        [min(w-1, w + shift()), min(h-1, h + shift())],
        [max(0, 0 + shift()), min(h-1, h + shift())]
    ])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    img_p = cv2.warpPerspective(img, M, (w,h), borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0))
    alpha_p = cv2.warpPerspective(alpha, M, (w,h), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return img_p, alpha_p

def place_on_background(rgb, alpha):
    # Create metallic-ish background with gradient and noise
    h,w = IMG_SIZE, IMG_SIZE

    base_color = np.array([30, 40, random.randint(30,70)], dtype=np.uint8)
    bg = np.ones((h,w,3), dtype=np.uint8) * base_color

    gx = np.linspace(0, 1, w)
    gy = np.linspace(0, 1, h)
    Gx, Gy = np.meshgrid(gx, gy)
    grd = (0.6*Gx + 0.4*Gy).reshape(h,w,1)
    bg = np.clip(bg.astype(np.float32) * (0.7 + 0.6*grd), 0, 255).astype(np.uint8)

    bg = cv2.GaussianBlur(bg, (5,5), 0)
    noise = (np.random.randn(h,w) * 10).astype(np.int16)
    for c in range(3):
        ch = bg[:,:,c].astype(np.int16) + noise
        bg[:,:,c] = np.clip(ch, 0, 255).astype(np.uint8)

    # --- FIX: shape must be placed inside a full-size canvas ---
    rh, rw = rgb.shape[:2]

    # create canvas for shape
    shape_canvas = np.zeros((h,w,3), dtype=np.uint8)
    mask_canvas  = np.zeros((h,w), dtype=np.uint8)

    # random placement
    x = random.randint(0, w - rw)
    y = random.randint(0, h - rh)

    shape_canvas[y:y+rh, x:x+rw] = rgb
    mask_canvas[y:y+rh, x:x+rw] = alpha

    # composite
    mask_f = (mask_canvas.astype(np.float32)/255.0)[:,:,None]
    inv = 1.0 - mask_f

    out = (bg.astype(np.float32) * inv + shape_canvas.astype(np.float32) * mask_f).astype(np.uint8)

    return out

def add_post_effects(img):
    # metal texture overlay
    # add small gaussian noise
    h,w = img.shape[:2]
    noise = (np.random.randn(h,w,3) * np.random.uniform(2,12)).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    # occasional scratches
    if random.random() > 0.45:
        img = add_scratches_cv(img, count=random.randint(2,8))
    # occasional dirt
    if random.random() > 0.45:
        img = add_dirt_cv(img, level=random.uniform(0.01, 0.04))
    # final blur/jitter
    if random.random() > 0.6:
        k = random.choice([1,3])
        img = cv2.GaussianBlur(img, (k,k), 0)
    # color jitter via PIL for brightness/contrast
    pil = Image.fromarray(img)
    enh_b = ImageEnhance.Brightness(pil).enhance(random.uniform(0.8,1.2))
    enh_c = ImageEnhance.Contrast(enh_b).enhance(random.uniform(0.85,1.25))
    img = np.array(enh_c)
    return img

def add_scratches_cv(img, count=5):
    out = img.copy()
    h,w = out.shape[:2]
    for _ in range(count):
        x1 = random.randint(int(0.05*w), int(0.9*w))
        y1 = random.randint(int(0.05*h), int(0.9*h))
        length = random.randint(int(0.05*w), int(0.6*w))
        angle = random.uniform(-25, 25)
        x2 = int(x1 + length * math.cos(math.radians(angle)))
        y2 = int(y1 + length * math.sin(math.radians(angle)))
        thickness = random.randint(1,2)
        # dark core + bright edge
        cv2.line(out, (x1,y1), (x2,y2), (10,10,10), thickness+1, cv2.LINE_AA)
        cv2.line(out, (x1,y1), (x2,y2), (220,220,220), max(1, thickness), cv2.LINE_AA)
    return out

def add_dirt_cv(img, level=0.02):
    out = img.copy().astype(np.float32)
    h,w = out.shape[:2]
    n = int(h*w*level/100)
    for _ in range(n):
        cx = random.randint(0,w-1)
        cy = random.randint(0,h-1)
        r = random.randint(3, int(min(w,h)*0.04))
        Y, X = np.ogrid[:h, :w]
        mask = ((X-cx)**2 + (Y-cy)**2) <= r*r
        out[mask] = out[mask] * np.random.uniform(0.6, 0.95)
    return np.clip(out,0,255).astype(np.uint8)

def generate_for_class(name, base_pil):
    rgb_base, alpha_base = rgba_to_cv(base_pil)
    # scale base to IMG_SIZE first
    rgb_base = cv2.resize(rgb_base, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
    alpha_base = cv2.resize(alpha_base, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_NEAREST)
    out_folder = os.path.join(OUT_DIR, name)
    os.makedirs(out_folder, exist_ok=True)

    for i in range(PER_CLASS):
        # start from base scaled, apply transforms
        rgb = rgb_base.copy()
        alpha = alpha_base.copy()

        # random small crop/scale
        s = random.uniform(0.9, 1.05)
        new_sz = int(IMG_SIZE * s)
        
        # Redimensionam imaginea curenta
        rgb = cv2.resize(rgb, (new_sz, new_sz), interpolation=cv2.INTER_AREA)
        alpha = cv2.resize(alpha, (new_sz, new_sz), interpolation=cv2.INTER_NEAREST)

        # --- FIX START ---
        # Verificam daca imaginea este mai mica sau mai mare decat canvas-ul (384px)
        if new_sz <= IMG_SIZE:
            # CAZ 1: Imaginea e mai mica -> O punem pe un canvas negru (Padding)
            canvas = np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.uint8)
            amask = np.zeros((IMG_SIZE, IMG_SIZE), dtype=np.uint8)
            
            # Putem alege pozitia random doar daca exista spatiu
            max_offset = IMG_SIZE - new_sz
            if max_offset > 0:
                x = random.randint(0, max_offset)
                y = random.randint(0, max_offset)
            else:
                x, y = 0, 0 # Se potriveste perfect

            canvas[y:y+new_sz, x:x+new_sz] = rgb
            amask[y:y+new_sz, x:x+new_sz] = alpha
            rgb, alpha = canvas, amask
            
        else:
            # CAZ 2: Imaginea e mai mare (Zoom in) -> Facem Crop
            # Trebuie sa taiem o bucata de 384x384 din imaginea mare
            max_offset = new_sz - IMG_SIZE
            x = random.randint(0, max_offset)
            y = random.randint(0, max_offset)
            
            rgb = rgb[y:y+IMG_SIZE, x:x+IMG_SIZE]
            alpha = alpha[y:y+IMG_SIZE, x:x+IMG_SIZE]
        # --- FIX END ---

        # rotations/perspective
        if random.random() > 0.3:
            rgb, alpha = random_scale_rotate(rgb, alpha)
        if random.random() > 0.4:
            rgb, alpha = apply_perspective(rgb, alpha, max_shift=18)

        # place on background
        composed = place_on_background(rgb, alpha)

        # post effects
        final = add_post_effects(composed)

        # final resize and optional small sharpening
        final = cv2.resize(final, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)
        if random.random() > 0.7:
            kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
            final = cv2.filter2D(final, -1, kernel)

        fname = f"{name}_{i:04d}.png"
        cv2.imwrite(os.path.join(out_folder, fname), final)

    print(f"Generated {PER_CLASS} images for {name} -> {out_folder}")

def main():
    # load all bases
    for cls in ["usa_stanga","usa_dreapta","aripa","capota","portbagaj"]:
        base = load_base(cls)
        generate_for_class(cls, base)

if __name__ == "__main__":
    main()
