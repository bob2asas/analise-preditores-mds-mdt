# =====================================================================
# overlays.py — contexto desenhado sobre o 3D
# Converte bairros, BR-101/avenidas e o zoológico (arquivos osm_ do
# OpenStreetMap) para as coordenadas da cena 3D e gera o mapa simples
# de localização (inset.svg).
# =====================================================================
import json, pickle, numpy as np
from shapely.geometry import LineString, box, Point, MultiLineString
from shapely.ops import transform, unary_union
from pyproj import Transformer
d=pickle.load(open('ctx.pkl','rb')); polys=d['polys']; tile=d['tile']; zoo=d['zoo']
ctx=json.load(open("/mnt/user-data/uploads/CDG -TRABALHO/analise_preditores/osm_contexto.json"))
T=Transformer.from_crs('EPSG:4326','EPSG:31985',always_xy=True).transform
x0,y0=282942.848473,9117554.033807; WX,WY=3540,2400
tbox=box(x0,y0-WY,x0+WX,y0)
loc=lambda g: transform(lambda x,y,z=None:(np.asarray(x)-x0,y0-np.asarray(y)),transform(T,g))  # local: x east, y south (row dir)
def lines(g):
    g=g if g.geom_type.startswith('Multi') or g.geom_type=='GeometryCollection' else [g]
    out=[]
    for p in (g.geoms if hasattr(g,'geoms') else g):
        if p.is_empty: continue
        if p.geom_type=='LineString': out.append([[round(a,1),round(b,1)] for a,b in p.coords])
        elif p.geom_type=='MultiLineString': out+= [[[round(a,1),round(b,1)] for a,b in q.coords] for q in p.geoms]
    return out
ov={'bairros':[], 'labels':[], 'roads':[]}
for (n,l),p in polys.items():
    if l!='10': continue
    pu=transform(T,p)
    if not pu.intersects(tbox): continue
    bnd=pu.boundary.intersection(tbox)
    ov['bairros'].append(lines(loc(transform(lambda x,y,z=None:(x,y),bnd)) if False else transform(lambda x,y,z=None:(np.asarray(x)-x0,y0-np.asarray(y)),bnd)))
    ip=pu.intersection(tbox)
    if ip.area/tbox.area>0.03:
        c=ip.representative_point(); ov['labels'].append({'t':n,'x':round(c.x-x0,1),'y':round(y0-c.y,1),'k':'bairro'})
for e in ctx['elements']:
    if e['type']=='way' and e.get('tags',{}).get('highway') in ('trunk','motorway'):
        l=transform(T,LineString([(p['lon'],p['lat']) for p in e['geometry']]))
        if l.intersects(tbox):
            ov['roads'].append(lines(transform(lambda x,y,z=None:(np.asarray(x)-x0,y0-np.asarray(y)),l.intersection(tbox))))
# BR-101 label: midpoint of longest road piece
allr=[seg for r in ov['roads'] for seg in r]
if allr:
    s=max(allr,key=len); m=s[len(s)//2]; ov['labels'].append({'t':'BR-101','x':m[0],'y':m[1],'k':'road'})
zc=transform(T,zoo.centroid)
ov['zoo']={'x':round(zc.x-x0,1),'y':round(y0-zc.y,1),'dist':round(transform(T,zoo).distance(tbox))}
ov['bairros']=[seg for b in ov['bairros'] for seg in b]
json.dump(ov,open('overlays.json','w'))
print(len(ov['bairros']),len(ov['roads']),ov['labels'],ov['zoo'])
# ---- inset SVG (lon/lat, equirect)
ext=box(-35.02,-8.08,-34.86,-7.93)
W,H=300,300*(0.15/0.16)
def P(lon,lat): return ((lon+35.02)/0.16*W,(-7.93-lat)/0.15*H)
def path(g):
    out=''
    for p in (g.geoms if hasattr(g,'geoms') else [g]):
        if p.is_empty: continue
        for ring in [p.exterior]:
            pts=[P(x,y) for x,y in ring.coords]; out+='M'+'L'.join(f'{a:.1f},{b:.1f}' for a,b in pts)+'Z'
    return out
svg=[f'<svg viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="Localização da área de estudo em Recife">']
svg.append(f'<rect width="{W:.0f}" height="{H:.0f}" fill="#16324a"/>')
for (n,l),p in polys.items():
    if l=='8':
        g=p.intersection(ext); svg.append(f'<path d="{path(g)}" fill="{"#262a2c" if n=="Recife" else "#202426"}" stroke="#6b6a64" stroke-width="1"/>')
for (n,l),p in polys.items():
    if l=='10':
        g=p.intersection(ext); svg.append(f'<path d="{path(g)}" fill="none" stroke="#3a3e40" stroke-width=".6"/>')
for e in ctx['elements']:
    if e['type']=='way' and e.get('tags',{}).get('highway') in ('trunk','motorway'):
        pts=[P(p['lon'],p['lat']) for p in e['geometry']]
        svg.append('<polyline points="'+' '.join(f'{a:.1f},{b:.1f}' for a,b in pts)+'" fill="none" stroke="#c9a24a" stroke-width="1.2" opacity=".8"/>')
zx,zy=P(*zoo.centroid.coords[0]); svg.append(f'<circle cx="{zx:.1f}" cy="{zy:.1f}" r="3.5" fill="#3fc48f"/><text x="{zx+6:.1f}" y="{zy+12:.1f}" fill="#cfcec7" font-size="10">Zoo Dois Irmãos</text>')
tx0,ty0=P(-34.9693,-7.9787); tx1,ty1=P(-34.9369,-8.0005)
svg.append(f'<rect x="{tx0:.1f}" y="{ty0:.1f}" width="{tx1-tx0:.1f}" height="{ty1-ty0:.1f}" fill="#e66767" fill-opacity=".25" stroke="#e66767" stroke-width="2"/>')
for t,lon,lat in [('RECIFE',-34.905,-8.06),('CAMARAGIBE',-35.0,-8.0),('OLINDA',-34.875,-7.99)]:
    x,y=P(lon,lat); svg.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="#9a998f" font-size="11" font-weight="600" letter-spacing="1">{t}</text>')
svg.append(f'<text x="{tx1+4:.1f}" y="{ty0+10:.1f}" fill="#f0efec" font-size="10.5" font-weight="600">área 3D</text>')
svg.append('</svg>')
open('inset.svg','w').write(''.join(svg)); print('svg bytes',len(''.join(svg)))
