# =====================================================================
# ctx.py — onde fica a área de estudo
# Cruza a quadrícula com os bairros do OpenStreetMap para calcular quanto da
# área cai em cada bairro (61% Guabiraba, 17% Dois Irmãos, 18% Aldeia) e mede
# a distância até o Zoológico. Salva tudo em ctx.pkl para os outros scripts.
# =====================================================================
import json, numpy as np
from shapely.geometry import LineString, Polygon, box, mapping, MultiLineString
from shapely.ops import linemerge, polygonize, unary_union, transform
from pyproj import Transformer
U="/mnt/user-data/uploads/CDG -TRABALHO/analise_preditores/"
lim=json.load(open(U+'osm_limites.json')); ctx=json.load(open(U+'osm_contexto.json')); c2=json.load(open(U+'osm_contexto2.json'))
def relpoly(e):
    ls=[LineString([(p['lon'],p['lat']) for p in m['geometry']]) for m in e['members'] if m.get('role')=='outer' and m.get('geometry')]
    return unary_union(list(polygonize(unary_union(ls))))
tile=box(-34.9693,-8.0005,-34.9369,-7.9787)
polys={}
for e in lim['elements']:
    n=e['tags']['name']; lvl=e['tags']['admin_level']
    try: p=relpoly(e)
    except Exception as ex: print('fail',n,ex); continue
    if p.is_empty: print('empty',n); continue
    polys.setdefault((n,lvl),[]).append(p)
polys={k:unary_union(v) for k,v in polys.items()}
print('Recife area ok', polys[('Recife','8')].area>0)
inter=[]
for (n,l),p in polys.items():
    if l=='10' and p.intersects(tile):
        a=p.intersection(tile).area/tile.area
        if a>0.005: inter.append((n,round(a*100,1)))
print(sorted(inter,key=lambda x:-x[1]))
zoo=[e for e in c2['elements'] if e.get('tags',{}).get('tourism')=='zoo'][0]
zp=Polygon([(p['lon'],p['lat']) for p in zoo['geometry']]); print('zoo centroid',zp.centroid.coords[0], 'dist to tile km', zp.distance(tile)*111)
roads=[]
for e in ctx['elements']:
    if e['type']=='way' and e.get('tags',{}).get('highway') in ('trunk','primary','motorway'):
        l=LineString([(p['lon'],p['lat']) for p in e['geometry']])
        if l.intersects(tile.buffer(0.002)): roads.append((e['tags'].get('ref') or e['tags'].get('name'), e['tags']['highway']))
print(set(roads))
import pickle; pickle.dump({'polys':polys,'zoo':zp,'tile':tile},open('ctx.pkl','wb'))
