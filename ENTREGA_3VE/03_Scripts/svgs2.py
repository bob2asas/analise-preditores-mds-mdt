# =====================================================================
# svgs2.py — diagramas das caixas de ajuda (parte 2)
# Esquemas de Hansen, declividade, MapBiomas, dossel Meta e HEM.
# Acrescenta os desenhos ao svgs.json.
# =====================================================================
import json
T='font-family="system-ui,Segoe UI,sans-serif"'
def tree(x,y,h,r=12):  # trunk base at y, height h
    return f'<rect x="{x-2.5}" y="{y-h*0.45}" width="5" height="{h*0.45}" fill="#6b4a2b"/><circle cx="{x}" cy="{y-h*0.45-r*0.6}" r="{r}" fill="#2f7d4f"/>'
# Hansen: 30 m cell grid with % cover
cells=[(0,'0%'),(1,'40%'),(2,'85%'),(3,'100%')]
g=''
for i,(k,lab) in enumerate(cells):
    x=14+i*66; g+=f'<rect x="{x}" y="34" width="58" height="58" fill="#1f2a22" stroke="#5a5f62"/>'
    n=[0,2,4,5][i]
    pos=[(14,14),(42,14),(28,29),(14,43),(42,43)]
    for (a,b) in pos[:n]: g+=f'<circle cx="{x+a}" cy="{34+b}" r="9" fill="#2f7d4f"/>'
    g+=f'<text x="{x+29}" y="108" font-size="11" fill="#f0efec" text-anchor="middle" font-weight="600">{lab}</text>'
hansen=f'''<svg viewBox="0 0 280 140" {T}><rect width="280" height="140" fill="#15181a"/>
<text x="140" y="20" font-size="10.5" fill="#b9b8b0" text-anchor="middle">Células de 30 m: % com árvores &gt; 5 m (2000)</text>{g}
<text x="140" y="130" font-size="10" fill="#9a998f" text-anchor="middle">Mais cobertura = mais copa somada ao MDS</text></svg>'''
# Declividade: radar oblique onto slope, shadow & distortion
decl=f'''<svg viewBox="0 0 280 140" {T}><rect width="280" height="140" fill="#15181a"/>
<path d="M0 118 L90 118 L170 48 L200 48 L280 118 Z" fill="#3a3326"/><path d="M0 118 L90 118 L170 48 L200 48 L280 118" stroke="#c8a477" stroke-width="3" fill="none"/>
<rect x="8" y="10" width="26" height="12" rx="2" fill="#9ec5f4"/><text x="40" y="20" font-size="10.5" fill="#d8d7d0">satélite radar (visada inclinada)</text>
<g stroke="#9ec5f4" stroke-width="1.6" stroke-dasharray="4 3"><line x1="30" y1="24" x2="128" y2="84"/><line x1="30" y1="24" x2="168" y2="50"/><line x1="30" y1="24" x2="240" y2="83"/></g>
<path d="M200 48 L280 118 L280 118 L234 118 Z" fill="#000" opacity=".45"/>
<text x="96" y="70" font-size="10.5" fill="#f4a582" font-weight="600" text-anchor="end">encosta</text><text x="96" y="83" font-size="10.5" fill="#f4a582" font-weight="600" text-anchor="end">comprimida</text><text x="258" y="104" font-size="10.5" fill="#9a998f" text-anchor="end">sombra</text>
<text x="8" y="132" font-size="10" fill="#9a998f">Encosta íngreme = mais erro do radar</text></svg>'''
# MapBiomas: classification grid
cols={'F':'#1f8d49','P':'#edde8e','U':'#d4271e','A':'#e974ed'}
grid=["FFFPPU","FFFFPU","FFPPAU","FFFPAA"]
g2=''
for r,row in enumerate(grid):
    for c,k in enumerate(row): g2+=f'<rect x="{12+c*21}" y="{22+r*21}" width="19" height="19" fill="{cols[k]}"/>'
mb=f'''<svg viewBox="0 0 280 140" {T}><rect width="280" height="140" fill="#15181a"/>{g2}
<g font-size="10.5" fill="#d8d7d0"><rect x="150" y="26" width="12" height="12" fill="#1f8d49"/><text x="168" y="36">floresta (= 1)</text>
<rect x="150" y="48" width="12" height="12" fill="#edde8e"/><text x="168" y="58">pastagem</text>
<rect x="150" y="70" width="12" height="12" fill="#e974ed"/><text x="168" y="80">agricultura</text>
<rect x="150" y="92" width="12" height="12" fill="#d4271e"/><text x="168" y="102">área urbana</text></g>
<text x="140" y="132" font-size="10" fill="#9a998f" text-anchor="middle">O modelo usa só: é floresta? (1 ou 0)</text></svg>'''
# Meta: bars LiDAR vs ETH vs Meta in tall forest (values from this study)
def bar(x,h,c,lab,val):
    y=118-h*2.6
    return f'<rect x="{x}" y="{y}" width="44" height="{118-y}" rx="3" fill="{c}"/><text x="{x+22}" y="{y-5}" font-size="11" fill="#f0efec" text-anchor="middle" font-weight="600">{val} m</text><text x="{x+22}" y="132" font-size="10.5" fill="#d8d7d0" text-anchor="middle">{lab}</text>'
meta=f'''<svg viewBox="0 0 280 140" {T}><rect width="280" height="140" fill="#15181a"/>
<text x="140" y="16" font-size="10.5" fill="#b9b8b0" text-anchor="middle">Altura da mata nas manchas vermelhas (média)</text>
{bar(40,31,'#c8a477','LiDAR (real)','31')}{bar(118,23,'#3987e5','ETH','23')}{bar(196,7,'#e66767','Meta','7')}
<line x1="20" y1="118" x2="262" y2="118" stroke="#5a5f62"/></svg>'''
# HEM: coherent vs noisy radar echo
hem=f'''<svg viewBox="0 0 280 140" {T}><rect width="280" height="140" fill="#15181a"/>
<path d="M14 50 q8 -16 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" stroke="#9ec5f4" stroke-width="2" fill="none"/>
<path d="M14 54 q8 -16 16 0 t16 0 t16 0 t16 0 t16 0 t16 0" stroke="#3987e5" stroke-width="2" fill="none"/>
<text x="66" y="80" font-size="11" fill="#f0efec" text-anchor="middle" font-weight="600">área aberta</text><text x="66" y="94" font-size="9.5" fill="#9a998f" text-anchor="middle">ecos iguais: HEM baixo</text>
<path d="M150 50 l6 -12 l5 18 l6 -20 l5 14 l6 -6 l5 16 l6 -22 l5 12 l6 -4 l5 14 l6 -18 l5 10 l6 -8 l5 12 l6 -10 l5 6" stroke="#f4a582" stroke-width="2" fill="none"/>
<path d="M150 56 l5 8 l6 -16 l5 4 l6 12 l5 -20 l6 10 l5 2 l6 -14 l5 18 l6 -8 l5 -6 l6 14 l5 -12 l6 4 l5 10 l6 -14" stroke="#e66767" stroke-width="2" fill="none"/>
<text x="212" y="80" font-size="11" fill="#f0efec" text-anchor="middle" font-weight="600">mata densa</text><text x="212" y="94" font-size="9.5" fill="#9a998f" text-anchor="middle">ecos embaralhados: HEM alto</text>
<text x="140" y="124" font-size="10" fill="#9a998f" text-anchor="middle">HEM: incerteza de altura do próprio Copernicus</text></svg>'''
d=json.load(open('svgs.json')); d.update({'hansen':hansen,'decl':decl,'mb':mb,'meta':meta,'hem':hem})
json.dump(d,open('svgs.json','w'),ensure_ascii=False)
open('preview2.html','w').write('<body style="background:#000;margin:0;display:grid;grid-template-columns:300px 300px;gap:10px;padding:10px">'+''.join(f'<div style="width:300px">{d[k]}</div>' for k in ['hansen','decl','mb','meta','hem'])+'</body>')
