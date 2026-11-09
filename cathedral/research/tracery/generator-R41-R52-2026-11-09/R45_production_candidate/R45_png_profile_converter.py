#!/usr/bin/env python3
"""R45 PNG outline intake: convert a user's chosen closed silhouette to an explicit,
scale-preserving R43_Section_V1 JSON; no invented historical dimensions.
Runs under system Python (OpenCV), NOT Blender embedded Python.
"""
from pathlib import Path
import argparse,hashlib,json,math
import cv2,numpy as np
from PIL import Image

def convert_png(path,output,*,profile_id,width_mm,depth_mm=None,rotation_deg=0,evidence_class='EXPERIMENTAL'):
    path=Path(path); output=Path(output)
    if not path.is_file():raise FileNotFoundError(path)
    if not (5<=width_mm<=1000):raise ValueError('WIDTH_MM_OUT_OF_RANGE')
    if depth_mm is not None and not (5<=depth_mm<=1000):raise ValueError('DEPTH_MM_OUT_OF_RANGE')
    if rotation_deg not in (0,90,180,270):raise ValueError('ROTATION_MUST_BE_90_DEG_STEPS')
    if evidence_class not in ('EXPERIMENTAL','SYNTHETIC','MEASURED_2D'):raise ValueError('UNSUPPORTED_EVIDENCE_CLASS')
    arr=cv2.imread(str(path),cv2.IMREAD_UNCHANGED)
    if arr is None:raise ValueError('UNREADABLE_PNG')
    if arr.ndim==2:
        gray=arr;alpha=None
    elif arr.shape[2] == 4:
        gray=cv2.cvtColor(arr[:,:,:3],cv2.COLOR_BGR2GRAY)
        alpha=arr[:,:,3]
    else:
        gray=cv2.cvtColor(arr[:,:,:3],cv2.COLOR_BGR2GRAY)
        alpha=None
    if rotation_deg:
        op={90:cv2.ROTATE_90_CLOCKWISE,180:cv2.ROTATE_180,270:cv2.ROTATE_90_COUNTERCLOCKWISE}[rotation_deg]
        gray=cv2.rotate(gray,op)
        if alpha is not None:alpha=cv2.rotate(alpha,op)
    if min(gray.shape)<100:raise ValueError('SOURCE_RESOLUTION_TOO_LOW')
    if alpha is not None and np.count_nonzero(alpha<248)>0.01*alpha.size:
        mask=np.uint8(alpha>=128)*255
        bg='alpha'
    else:
        border=np.concatenate([gray[:5,:].ravel(),gray[-5:,:].ravel(),gray[:,:5].ravel(),gray[:,-5:].ravel()])
        if np.std(border)>25:raise ValueError('NONUNIFORM_BORDER_BACKGROUND')
        background=float(np.median(border))
        mask=np.uint8(gray<170 if background>=190 else gray>85)*255
        bg='bright' if background>=190 else 'dark'
    if np.count_nonzero(mask)<0.005*mask.size or np.count_nonzero(mask)>0.90*mask.size:
        raise ValueError('EMPTY_OR_FILLED_IMAGE_MASK')
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contours=sorted(contours,key=cv2.contourArea,reverse=True)
    if not contours:raise ValueError('NO_CLOSED_CONTOUR')
    maximum=float(cv2.contourArea(contours[0]))
    if maximum<=100:raise ValueError('NO_MEANINGFUL_SHAPE')
    if len(contours)>1 and cv2.contourArea(contours[1])>maximum*.04:
        raise ValueError('MULTIPLE_FOREGROUND_SHAPES')
    c=contours[0]
    length=cv2.arcLength(c,True)
    eps=max(.65,min(1.55,length*.00065))
    approx=cv2.approxPolyDP(c,eps,True).reshape(-1,2)
    if not(8<=len(approx)<=2048):raise ValueError('INVALID_CONTOUR_COMPLEXITY')
    from shapely.geometry import Polygon
    poly=Polygon([(float(x),float(y)) for x,y in approx])
    if not poly.is_valid or poly.area<=0:raise ValueError('INVALID_PIXEL_POLYGON')
    xx=approx[:,0].astype(float); yy=approx[:,1].astype(float)
    span_x=float(xx.max()-xx.min());span_y=float(yy.max()-yy.min())
    if span_x<30 or span_y<30:raise ValueError('TINY_PIXEL_BBOX')
    factor=float(width_mm)/span_x
    actual_depth=span_y*factor
    if depth_mm is not None and abs(actual_depth-depth_mm)/depth_mm>.025:
        raise ValueError(f'ASPECT_RATIO_MISMATCH_expected_{depth_mm:g}_got_{actual_depth:.2f}')
    px=[(round(float((x-(xx.max()+xx.min())/2)*factor),5),
         round(float(((yy.max()+yy.min())/2-y)*factor),5)) for x,y in approx]
    signed=sum(x*v-u*y for (x,y),(u,v) in zip(px,px[1:]+px[:1]))*.5
    if signed<0:px.reverse()
    data={'format':'R43_Section_V1','units':'mm','profile_id':profile_id,
        'evidence_class':evidence_class,'source_document':str(path),
        'source_file_SHA256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'historical_3d_joint_certified':False,
        'closed_points_mm':px,'image_background_mode':bg,
        'requested_width_mm':width_mm,'derived_depth_mm':actual_depth,
        'source_pixel_size':[int(gray.shape[1]),int(gray.shape[0])],
        'method':'largest single closed foreground contour; uniform scale only; no front/rear historical claim'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(data,indent=2))
    return {'profile_id':profile_id,'vertices':len(px),'width_mm':float(width_mm),
            'depth_mm':actual_depth,'original_pixels':int(poly.area),
            'profile_area_mm2':abs(signed),'SHA256':data['source_file_SHA256'],'output':str(output)}
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--png',required=True);ap.add_argument('--out',required=True)
    ap.add_argument('--profile-id',required=True);ap.add_argument('--width-mm',type=float,required=True)
    ap.add_argument('--depth-mm',type=float)
    ap.add_argument('--rotate-deg',type=int,default=0)
    ap.add_argument('--evidence-class',default='EXPERIMENTAL')
    a=ap.parse_args()
    print('R45_PNG_INPUT',json.dumps(convert_png(a.png,a.out,profile_id=a.profile_id,width_mm=a.width_mm,
        depth_mm=a.depth_mm,rotation_deg=a.rotate_deg,evidence_class=a.evidence_class)))
