#!/usr/bin/env python3
"""
create_base_contours.py
Generează 5 imagini PNG (siluete cu fundal transparent) pentru clasele:
usa_stanga, usa_dreapta, aripa, capota, portbagaj
Salvează în: assets/base_contours/<clasa>.png
"""
import os
from PIL import Image, ImageDraw, ImageFilter

OUTDIR = "assets/base_contours"
IMG_SIZE = (1024, 1024)  # generăm mare pentru detaliu, apoi vom scala

os.makedirs(OUTDIR, exist_ok=True)

def save_png(mask, path):
    # mask: PIL Image mode "L" (0..255)
    # convert to RGBA with white shape and transparent background
    rgba = Image.new("RGBA", IMG_SIZE, (0,0,0,0))
    # paste white where mask>0
    white = Image.new("RGBA", IMG_SIZE, (255,255,255,255))
    rgba.paste(white, mask=mask)
    rgba.save(path)

def door_left():
    mask = Image.new("L", IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    w,h = IMG_SIZE
    # left door: trapezoid with slight curve simulate window/top gap
    pts = [
        (int(0.18*w), int(0.12*h)),
        (int(0.62*w), int(0.10*h)),
        (int(0.58*w), int(0.74*h)),
        (int(0.22*w), int(0.78*h))
    ]
    draw.polygon(pts, fill=255)
    # window cutout (negative)
    win_pts = [
        (int(0.24*w), int(0.18*h)),
        (int(0.56*w), int(0.16*h)),
        (int(0.52*w), int(0.34*h)),
        (int(0.28*w), int(0.36*h))
    ]
    draw.polygon(win_pts, fill=0)
    # handle hole (small round)
    draw.ellipse((int(0.55*w), int(0.44*h), int(0.57*w), int(0.46*h)), fill=0)
    # smooth edges
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    return mask

def door_right():
    mask = Image.new("L", IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    w,h = IMG_SIZE
    pts = [
        (int(0.38*w), int(0.10*h)),
        (int(0.82*w), int(0.12*h)),
        (int(0.78*w), int(0.78*h)),
        (int(0.42*w), int(0.74*h))
    ]
    draw.polygon(pts, fill=255)
    win_pts = [
        (int(0.44*w), int(0.16*h)),
        (int(0.76*w), int(0.18*h)),
        (int(0.72*w), int(0.36*h)),
        (int(0.48*w), int(0.34*h))
    ]
    draw.polygon(win_pts, fill=0)
    draw.ellipse((int(0.45*w), int(0.44*h), int(0.47*w), int(0.46*h)), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    return mask

def fender():
    mask = Image.new("L", IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    w,h = IMG_SIZE
    # aripa: curbată cu decupaj rotund pentru roată
    pts = [
        (int(0.10*w), int(0.6*h)),
        (int(0.92*w), int(0.6*h)),
        (int(0.82*w), int(0.22*h)),
        (int(0.42*w), int(0.18*h))
    ]
    draw.polygon(pts, fill=255)
    # wheel arch: subtract circle
    circle_bbox = (int(0.12*w), int(0.44*h), int(0.48*w), int(0.88*h))
    draw.ellipse(circle_bbox, fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(5))
    return mask

def hood():
    mask = Image.new("L", IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    w,h = IMG_SIZE
    # capotă: mare arc în jumătatea superioară
    bbox = (int(0.06*w), int(0.08*h), int(0.94*w), int(0.6*h))
    draw.pieslice(bbox, start=0, end=180, fill=255)
    # crest lines (subtract narrow)
    draw.rectangle((int(0.2*w), int(0.32*h), int(0.8*w), int(0.34*h)), fill=0)
    mask = mask.filter(ImageFilter.GaussianBlur(4))
    return mask

def trunk():
    mask = Image.new("L", IMG_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    w,h = IMG_SIZE
    # portbagaj: dreptunghi rotunjit, cu separatie linie
    bbox = (int(0.18*w), int(0.48*h), int(0.82*w), int(0.82*h))
    draw.rounded_rectangle(bbox, radius=int(0.04*w), fill=255)
    draw.rectangle((int(0.18*w), int(0.48*h), int(0.82*w), int(0.50*h)), fill=0)  # gap line
    mask = mask.filter(ImageFilter.GaussianBlur(3))
    return mask

masks = {
    "usa_stanga": door_left(),
    "usa_dreapta": door_right(),
    "aripa": fender(),
    "capota": hood(),
    "portbagaj": trunk()
}

for name, mask in masks.items():
    path = os.path.join(OUTDIR, f"{name}.png")
    save_png(mask, path)
    print("Saved", path)

print("Base contours created in:", OUTDIR)
