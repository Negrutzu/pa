#!/usr/bin/env python3
"""
generate_dataset_realistic.py

Generează imagini sintetice, detaliate și variate, pentru clasele:
- usa_stanga
- usa_dreapta
- aripa
- capota
- portbagaj

Dependințe: opencv-python, numpy
Rulează: python3 generate_dataset_realistic.py
"""
import os
import cv2
import numpy as np
from math import sin, cos, radians

# Configurație
OUTPUT = "data/raw/"
CLASSES = ["usa_stanga", "usa_dreapta", "aripa", "capota", "portbagaj"]
IMG_SIZE = 384                # dimensiune imagine finală (poți crește la 512 pentru mai mult detaliu)
PER_CLASS = 150               # câte imagini per clasă

np.random.seed(42)

# -----------------------
# Funcții utilitare
# -----------------------
def ensure_dirs():
    for cls in CLASSES:
        path = os.path.join(OUTPUT, cls)
        os.makedirs(path, exist_ok=True)

def random_light_variation(img):
    """Aplică un gradient de iluminare și un punct de reflexie specular pentru realism."""
    h, w = img.shape[:2]
    # Gradient linear (alegem o direcție random)
    angle = np.random.uniform(0, 360)
    gx = np.linspace(-1, 1, w)
    gy = np.linspace(-1, 1, h)
    X, Y = np.meshgrid(gx, gy)
    # rotire gradient
    th = radians(angle)
    grd = X * cos(th) + Y * sin(th)
    grd = (grd - grd.min()) / (grd.max() - grd.min())  # 0..1
    # contrast and offset random
    mult = np.random.uniform(0.6, 1.4)
    add = np.random.uniform(-0.15, 0.15)
    lighting = np.clip(grd * mult + add, 0.0, 1.0)
    # convert to 3 channel if needed
    if img.ndim == 2:
        img_f = img.astype(np.float32) * lighting
    else:
        img_f = img.astype(np.float32)
        for c in range(3):
            img_f[:, :, c] = img_f[:, :, c] * lighting
    # small specular highlight
    if np.random.rand() > 0.3:
        cx = int(w * np.random.uniform(0.3, 0.7))
        cy = int(h * np.random.uniform(0.2, 0.6))
        rx = int(w * np.random.uniform(0.05, 0.18))
        ry = int(h * np.random.uniform(0.02, 0.08))
        mask = np.zeros((h, w), dtype=np.float32)
        y, x = np.ogrid[:h, :w]
        mask = np.exp(-(((x-cx)**2)/(2*(rx**2)) + ((y-cy)**2)/(2*(ry**2))))
        spec_strength = np.random.uniform(0.2, 0.8)
        if img.ndim == 2:
            img_f += mask * 255 * spec_strength
        else:
            for c in range(3):
                img_f[:,:,c] += mask * 255 * spec_strength
    img_f = np.clip(img_f, 0, 255).astype(np.uint8)
    return img_f

def add_metal_texture(img, intensity=0.08):
    """Suprapune 'textură metalică' folosind zgomot gaussian + blur."""
    h, w = img.shape[:2]
    noise = np.random.randn(h, w).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0,0), sigmaX=3, sigmaY=3)
    noise = (noise - noise.min())/(noise.max()-noise.min())  # 0..1
    # scale noise to subtle contrast changes
    noise = (noise * 255 * intensity).astype(np.uint8)
    if img.ndim == 2:
        out = cv2.add(img, noise)
    else:
        out = img.copy()
        for c in range(3):
            out[:,:,c] = cv2.add(out[:,:,c], noise)
    return out

def add_scratches(img, count=6):
    """Desenează zgârieturi fine random, cu variabilitate în lungime, curbură și opacitate."""
    out = img.copy()
    h, w = out.shape[:2]
    for _ in range(count):
        # random start and end, mostly horizontal-ish on car panels
        x1 = int(np.random.uniform(0.05*w, 0.95*w))
        y1 = int(np.random.uniform(0.1*h, 0.9*h))
        length = int(np.random.uniform(0.1*w, 0.7*w))
        angle = np.random.uniform(-20, 20)  # slight tilt
        x2 = int(x1 + length * cos(radians(angle)))
        y2 = int(y1 + length * sin(radians(angle)))
        thickness = np.random.randint(1, 3)
        color = (np.random.randint(200,255),)*3 if out.ndim==3 else np.random.randint(200,255)
        # draw slightly blurred thin line to simulate scratch reflective edge + dark core
        cv2.line(out, (x1,y1), (x2,y2), (0,0,0) if out.ndim==3 else 0, thickness+1, cv2.LINE_AA)
        cv2.line(out, (x1,y1), (x2,y2), color, max(1, thickness-1), cv2.LINE_AA)
        # add local blur
        x_min = max(0, min(x1,x2)-5)
        x_max = min(w, max(x1,x2)+5)
        y_min = max(0, min(y1,y2)-5)
        y_max = min(h, max(y1,y2)+5)
        roi = out[y_min:y_max, x_min:x_max]
        if roi.size:
            roi = cv2.GaussianBlur(roi, (3,3), 0)
            out[y_min:y_max, x_min:x_max] = roi
    return out

def add_dirt_and_spots(img, level=0.02):
    """Adaugă pete și murdărie subtile."""
    out = img.copy().astype(np.float32)
    h,w = out.shape[:2]
    n_spots = int(h*w*level/1000) + np.random.randint(5,12)
    for _ in range(n_spots):
        cx = np.random.randint(0,w)
        cy = np.random.randint(0,h)
        rad = np.random.randint(2, int(min(h,w)*0.03))
        color = np.random.randint(10,60)  # dark spot
        mask = np.zeros((h,w), dtype=np.uint8)
        cv2.circle(mask, (cx,cy), rad, 255, -1)
        blurred = cv2.GaussianBlur(mask.astype(np.float32), (rad*2+1, rad*2+1), 0)
        if out.ndim==3:
            for c in range(3):
                out[:,:,c] = np.where(blurred>0, out[:,:,c] * (1 - 0.3*blurred/255.0) - color*(blurred/255.0)*0.2, out[:,:,c])
        else:
            out = np.where(blurred>0, out * (1 - 0.3*blurred/255.0) - color*(blurred/255.0)*0.2, out)
    out = np.clip(out, 0, 255).astype(np.uint8)
    return out

def perspective_transform(img, max_shift=30):
    """Aplică o transformare de perspectivă ușoară pentru variabilitate."""
    h,w = img.shape[:2]
    # four source points
    pts1 = np.float32([[0,0],[w,0],[w,h],[0,h]])
    # small random offsets
    shift = lambda : np.random.randint(-max_shift, max_shift)
    pts2 = np.float32([[max(0,0+shift()), max(0,0+shift())],
                       [min(w-1,w+shift()), max(0,0+shift())],
                       [min(w-1,w+shift()), min(h-1,h+shift())],
                       [max(0,0+shift()), min(h-1,h+shift())]])
    M = cv2.getPerspectiveTransform(pts1, pts2)
    warped = cv2.warpPerspective(img, M, (w,h), borderMode=cv2.BORDER_REPLICATE)
    return warped

# -----------------------
# Desene specifice pieselor
# -----------------------
def rounded_polygon(img, pts, color=(255,255,255)):
    """Desenare poligon cu colțuri rotunjite (apelăm fillPoly + blur pentru netezire)."""
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, [np.array(pts, dtype=np.int32)], (255,255,255))
    # erode/dilate to round corners
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    # combine mask
    if len(img.shape)==3:
        for c in range(3):
            img[:,:,c] = np.where(mask[:,:,0]>0, color[c], img[:,:,c])
    else:
        img = np.where(mask>0, 255, img)
    # slight blur to smooth edges
    img = cv2.GaussianBlur(img, (3,3), 0)
    return img

def draw_door_left(img):
    h,w = img.shape[:2]
    # trapezoid shape, slight inwards at bottom to simulate geometry
    pts = [(int(0.18*w), int(0.12*h)),
           (int(0.62*w), int(0.12*h)),
           (int(0.58*w), int(0.74*h)),
           (int(0.22*w), int(0.78*h))]
    img = rounded_polygon(img, pts)
    # handle - small rectangle with shadow + highlight
    hx = int(0.56*w); hy = int(0.46*h)
    cv2.rectangle(img, (hx,hy), (hx+10,hy+6), (30,30,30), -1)
    # highlight on handle
    cv2.rectangle(img, (hx+1,hy+1), (hx+8,hy+3), (180,180,180), -1)
    # seam line (door gap)
    x = int(0.18*w)
    cv2.line(img, (x, int(0.12*h)), (x, int(0.78*h)), (30,30,30), 1)
    return img

def draw_door_right(img):
    h,w = img.shape[:2]
    pts = [(int(0.38*w), int(0.12*h)),
           (int(0.82*w), int(0.12*h)),
           (int(0.78*w), int(0.78*h)),
           (int(0.42*w), int(0.74*h))]
    img = rounded_polygon(img, pts)
    # handle on left side of this door
    hx = int(0.44*w); hy = int(0.46*h)
    cv2.rectangle(img, (hx,hy), (hx+10,hy+6), (30,30,30), -1)
    cv2.rectangle(img, (hx+1,hy+1), (hx+8,hy+3), (180,180,180), -1)
    # seam line
    x = int(0.82*w)
    cv2.line(img, (x, int(0.12*h)), (x, int(0.78*h)), (30,30,30), 1)
    return img

def draw_fender(img):
    h,w = img.shape[:2]
    pts = [(int(0.12*w), int(0.6*h)),
           (int(0.9*w), int(0.6*h)),
           (int(0.8*w), int(0.24*h)),
           (int(0.4*w), int(0.18*h))]
    img = rounded_polygon(img, pts)
    # edge seam
    cv2.line(img, (int(0.4*w), int(0.18*h)), (int(0.8*w), int(0.24*h)), (30,30,30), 2)
    return img

def draw_hood(img):
    h,w = img.shape[:2]
    # hood as big arc/ellipse across top half
    cv2.ellipse(img, (int(w/2), int(0.35*h)), (int(0.46*w), int(0.35*h)), 0, 0, 180, (255,255,255), -1)
    # crease lines
    cv2.line(img, (int(w*0.2), int(h*0.35)), (int(w*0.8), int(h*0.35)), (200,200,200), 1)
    return img

def draw_trunk(img):
    h,w = img.shape[:2]
    pts = [(int(0.18*w), int(0.48*h)),
           (int(0.82*w), int(0.48*h)),
           (int(0.82*w), int(0.78*h)),
           (int(0.18*w), int(0.78*h))]
    img = rounded_polygon(img, pts)
    cv2.line(img, (int(0.18*w), int(0.48*h)), (int(0.82*w), int(0.48*h)), (30,30,30), 2)
    return img

# -----------------------
# Funcție principală de generare
# -----------------------
def generate_one(cls_name):
    # blank dark metallic background
    base = np.full((IMG_SIZE, IMG_SIZE, 3), 30, dtype=np.uint8)

    # draw shape on top
    if cls_name == "usa_stanga":
        img = draw_door_left(base.copy())
    elif cls_name == "usa_dreapta":
        img = draw_door_right(base.copy())
    elif cls_name == "aripa":
        img = draw_fender(base.copy())
    elif cls_name == "capota":
        img = draw_hood(base.copy())
    elif cls_name == "portbagaj":
        img = draw_trunk(base.copy())
    else:
        img = base.copy()

    # add metal texture
    img = add_metal_texture(img, intensity=np.random.uniform(0.03, 0.12))

    # apply random lighting gradient and speculars
    img = random_light_variation(img)

    # add scratches randomly
    if np.random.rand() > 0.4:
        img = add_scratches(img, count=np.random.randint(3,12))

    # add dirt spots sometimes
    if np.random.rand() > 0.5:
        img = add_dirt_and_spots(img, level=np.random.uniform(0.01,0.05))

    # slight gaussian blur to simulate lens
    if np.random.rand() > 0.6:
        k = np.random.choice([1,3])
        img = cv2.GaussianBlur(img, (k,k), 0)

    # perspective transform occasionally
    if np.random.rand() > 0.3:
        img = perspective_transform(img, max_shift=24)

    # small rotation
    ang = np.random.uniform(-6, 6)
    Mrot = cv2.getRotationMatrix2D((IMG_SIZE/2, IMG_SIZE/2), ang, 1.0)
    img = cv2.warpAffine(img, Mrot, (IMG_SIZE, IMG_SIZE), borderMode=cv2.BORDER_REFLECT)

    # final light/color jitter
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)

    # resize down/up to target to introduce slight aliasing
    final = cv2.resize(img, (IMG_SIZE, IMG_SIZE), interpolation=cv2.INTER_AREA)

    return final

def generate_dataset():
    ensure_dirs()
    for cls in CLASSES:
        folder = os.path.join(OUTPUT, cls)
        print("Generating class:", cls)
        for i in range(PER_CLASS):
            img = generate_one(cls)
            # filename uniqueness
            fname = f"{cls}_{i:04d}.png"
            path = os.path.join(folder, fname)
            cv2.imwrite(path, img)
        print(f"Saved {PER_CLASS} images to {folder}")

if __name__ == "__main__":
    generate_dataset()
    print("All done.")
