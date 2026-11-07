#!/usr/bin/env python3
"""prep_page.py PDF PAGE OUT.png --rotate {0,90,-90} --box x0 y0 x1 y1 (fractions of the page)
Renders a page at its native resolution, evens the paper, keeps faint line pixels that
join solid lines, upscales 2x, bridges small gaps and gives lines a steady width."""
import argparse, subprocess, tempfile, os, glob
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
ap=argparse.ArgumentParser(); ap.add_argument('pdf'); ap.add_argument('page',type=int); ap.add_argument('out')
ap.add_argument('--rotate',type=int,default=0); ap.add_argument('--box',type=float,nargs=4,default=[0,0,1,1])
ap.add_argument('--dpi',type=float,default=350.5)
a=ap.parse_args()
with tempfile.TemporaryDirectory() as t:
    subprocess.run(['pdftoppm','-f',str(a.page),'-l',str(a.page),'-r',str(a.dpi),'-gray','-png',a.pdf,t+'/p'],check=True)
    im=Image.open(glob.glob(t+'/p*.png')[0]).convert('L')
if a.rotate: im=im.rotate(a.rotate,expand=True)
W,H=im.size
x0,y0,x1,y1=[int(v) for v in (a.box[0]*W,a.box[1]*H,a.box[2]*W,a.box[3]*H)]
im=im.crop((max(0,x0-60),max(0,y0-60),min(W,x1+60),min(H,y1+60)))
g=np.asarray(im,float); bg=np.asarray(im.filter(ImageFilter.GaussianBlur(40)),float)
n=np.clip(g/np.maximum(bg,1)*255,0,255)
c=Image.fromarray(n.astype('uint8')); c=c.resize((c.size[0]*2,c.size[1]*2),Image.LANCZOS)
g=np.asarray(c,float)
strong=g<175; weak=g<222
lab,k=ndi.label(weak,structure=np.ones((3,3),int))
keep=np.zeros(k+1,bool); keep[1:]=ndi.maximum(strong,lab,range(1,k+1)); ink=keep[lab]
s8=ndi.generate_binary_structure(2,2)
ink=ndi.binary_closing(ink,structure=s8,iterations=2); ink=ndi.binary_dilation(ink,structure=s8,iterations=1)
lab,k=ndi.label(ink,structure=np.ones((3,3),int)); sz=ndi.sum(ink,lab,range(1,k+1))
keep=np.zeros(k+1,bool); keep[1:]=sz>=900; ink=keep[lab]
ink=ink[120:-120,120:-120]
Image.fromarray(((~ink)*255).astype('uint8')).save(a.out); print(a.out,ink.shape[::-1])
