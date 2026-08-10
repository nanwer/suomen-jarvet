#!/usr/bin/env python3
"""Generate PWA app icons (Pillow). Run with a Python that has Pillow."""
from PIL import Image, ImageDraw
import os
BASE=os.path.dirname(os.path.abspath(__file__))
NAVY=(11,18,32,255); AMBER=(245,158,11,255); BLUE1=(74,163,255,255); BLUE2=(134,198,255,255)

def motif(d, size, k):
    cx=cy=size//2; s=size/512*k
    d.ellipse([cx-168*s,cy-168*s,cx+168*s,cy+168*s], outline=BLUE2, width=max(2,int(12*s)))
    d.ellipse([cx-112*s,cy-112*s,cx+112*s,cy+112*s], outline=BLUE1, width=max(2,int(14*s)))
    d.ellipse([cx-50*s,cy-50*s,cx+50*s,cy+50*s], fill=AMBER)

def make(size, rounded=True, k=1.0):
    img=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(img)
    if rounded: d.rounded_rectangle([0,0,size-1,size-1], radius=int(size*0.20), fill=NAVY)
    else: d.rectangle([0,0,size,size], fill=NAVY)
    motif(d, size, k); return img

# supersample for crisp edges: draw at 4x then downscale
def hi(size, rounded=True, k=1.0):
    return make(size*4, rounded, k).resize((size,size), Image.LANCZOS)

hi(512, True, 1.0).save(f"{BASE}/icon-512.png")
hi(192, True, 1.0).save(f"{BASE}/icon-192.png")
hi(512, False, 0.78).save(f"{BASE}/icon-maskable-512.png")   # full-bleed, safe zone
hi(180, False, 1.0).save(f"{BASE}/apple-touch-icon.png")     # iOS rounds corners itself
print("icons written:", [f for f in os.listdir(BASE) if f.endswith('.png') and 'icon' in f or f.startswith('apple')])
