# =====================================================================
# zoommap.py — mapa "Onde fica" com zoom do Brasil até a área
# Usa os limites FAO GAUL (Brasil, estados, municípios de PE), os bairros e
# vias do OpenStreetMap e o emblema do 3º CGEO (cgeo.png) para gerar um mapa
# SVG com 4 níveis de aproximação: Brasil → Pernambuco → Recife → Área 3D.
# =====================================================================
import json, pickle, math
from shapely.geometry import box, shape, Polygon, MultiPolygon
G=json.load(open('/mnt/user-data/uploads/CDG -TRABALHO/analise_preditores/gaul_contexto.json'))
C=pickle.load(open('ctx.pkl','rb')); polys=C['polys']; zoo=C['zoo']; tile=C['tile']
U="/mnt/user-data/uploads/CDG -TRABALHO/analise_preditores/"
ctx=json.load(open(U+'osm_contexto.json'))
K=0.97
X=lambda lon:(lon+82)*100*K; Y=lambda lat:(13-lat)*100
def ring(r,dec): 
    return 'M'+'L'.join(f'{X(x):.{dec}f},{Y(y):.{dec}f}' for x,y in r)+'Z'
def gpath(polys,dec=1):  # GAUL list of polygons (list of rings)
    return ''.join(ring(p[0],dec) for p in polys if p and len(p[0])>2)
def spath(g,dec=2):
    out=''
    for p in (g.geoms if hasattr(g,'geoms') else [g]):
        if p.is_empty or p.geom_type!='Polygon': continue
        out+=ring(p.exterior.coords,dec)
    return out
NS='vector-effect="non-scaling-stroke"'
s=[]
s.append('<rect x="0" y="0" width="6000" height="6000" fill="#16324a"/>')
for f in G['l0']:
    br=f['p']['ADM0_NAME']=='Brazil'
    s.append(f'<path d="{gpath(f["g"])}" fill="{"#262a2c" if br else "#1d2022"}" stroke="#5d5f5a" stroke-width="{1.2 if br else .8}" {NS}/>')
st=[]
for f in G['l1']:
    pe=f['p']['ADM1_NAME']=='Pernambuco'
    s.append(f'<path d="{gpath(f["g"])}" fill="{"#3a4a35" if pe else "none"}" stroke="{"#9bd36f" if pe else "#4a4d48"}" stroke-width="{1.4 if pe else .6}" {NS} class="{"pe" if pe else ""}"/>')
mun=''.join(gpath(f['g'],2) for f in G['l2'])
s.append(f'<path class="z1" d="{mun}" fill="none" stroke="#4d524c" stroke-width=".6" {NS}/>')
rec=[f for f in G['l2'] if f['p']['ADM2_NAME'] in ('Recife',)]
s.append(f'<path class="z1" d="{gpath(rec[0]["g"],2)}" fill="#33402f" stroke="#9bd36f" stroke-width="1.2" {NS}/>')
ext=box(-35.06,-8.12,-34.82,-7.9)
b=''.join(spath(p.intersection(ext).simplify(0.00004),3) for (n,l),p in polys.items() if l=='10')
s.append(f'<path class="z2" d="{b}" fill="none" stroke="#3d4240" stroke-width=".6" {NS}/>')
rd=''
for e in ctx['elements']:
    if e['type']=='way' and e.get('tags',{}).get('highway') in ('trunk','motorway'):
        rd+='M'+'L'.join(f'{X(p["lon"]):.3f},{Y(p["lat"]):.3f}' for p in e['geometry'])
s.append(f'<path class="z2" d="{rd}" fill="none" stroke="#c9a24a" stroke-width="1.3" opacity=".85" {NS}/>')
zx,zy=X(zoo.centroid.x),Y(zoo.centroid.y)
s.append(f'<circle class="z2 sc" data-r="3.5" cx="{zx:.3f}" cy="{zy:.3f}" r="1" fill="#3fc48f"/>')
x0,y0,x1,y1=X(-34.9693),Y(-7.9787),X(-34.9369),Y(-8.0005)
s.append(f'<rect x="{x0:.3f}" y="{y0:.3f}" width="{x1-x0:.3f}" height="{y1-y0:.3f}" fill="#e66767" fill-opacity=".3" stroke="#e66767" stroke-width="2" {NS}/>')
cx,cy=(x0+x1)/2,(y0+y1)/2
s.append(f'<circle id="zmPulse" cx="{cx:.3f}" cy="{cy:.3f}" r="1" fill="none" stroke="#e66767" stroke-width="2" {NS}/>')
s.append(f'<circle id="zmDot" cx="{cx:.3f}" cy="{cy:.3f}" r="1" fill="#e66767"/>')
L=[('BRASIL',-52,-10,0,0.9,13,'#c8c7bf'),('Oceano Atlântico',-38,-27,0,0.9,10,'#7f9fb8'),('PERNAMBUCO',-38.3,-8.55,0.55,1.6,13,'#cfe8bd'),('Pernambuco',-37.5,-6.2,0,0.55,10.5,'#cfe8bd'),
 ('Recife',-34.93,-8.13,1.4,2.3,12,'#cfe8bd'),('Grande Recife',-35.3,-7.75,1.0,1.7,11,'#cfe8bd'),('Olinda',-34.86,-7.99,2.3,3.1,10.5,'#9a998f'),('CAMARAGIBE',-35.0,-8.0,2.4,3.1,10.5,'#9a998f'),('RECIFE',-34.905,-8.06,2.4,3.1,11,'#9a998f'),
 ('Zoo Dois Irmãos',-34.995,-8.0095,2.4,3.1,10,'#cfcec7'),('área 3D',-34.935,-7.982,1.8,3.1,10.5,'#f0efec')]
for t,lon,lat,a,bb,fs,c in L:
    s.append(f'<text class="lb" data-a="{a}" data-b="{bb}" data-fs="{fs}" x="{X(lon):.3f}" y="{Y(lat):.3f}" fill="{c}" font-weight="600" text-anchor="{"start" if t in ("área 3D","Zoo Dois Irmãos") else ("end" if t=="Olinda" else "middle")}" style="paint-order:stroke;stroke:#0e1012;stroke-width:3px;stroke-linejoin:round">{t}</text>')
import base64
from PIL import Image as _I
_im=_I.open('cgeo.png');_im.thumbnail((92,130));_im.save('cgeo_s.png',optimize=True)
cg=base64.b64encode(open('cgeo_s.png','rb').read()).decode()
s.append(f'<image class="emb" data-ax="{X(-34.8625):.3f}" data-ay="{Y(-7.9935):.3f}" data-w="24" data-h="34" data-a="2.3" data-b="3.1" href="data:image/png;base64,{cg}" preserveAspectRatio="xMidYMid meet"><title>3º Centro de Geoinformação (3º CGEO), Olinda</title></image>')
KF=[(-75,-34,-33,6),(-41.6,-9.7,-34.6,-7.0),(-35.25,-8.25,-34.75,-7.82),(-35.02,-8.08,-34.86,-7.93)]
kf=[[X((a+c)/2),Y((b+d)/2),max((X(c)-X(a)),(Y(b)-Y(d))*300/281)] for a,b,c,d in KF]
svg=f'<svg id="zmap" viewBox="0 0 300 281" width="300" height="281" role="img" aria-label="Localização da área de estudo: do Brasil até Recife" style="touch-action:none">'+''.join(s)+'</svg>'
ctrl='''<div class="zmc"><button data-t="0">Brasil</button><button data-t="1">PE</button><button data-t="2">Recife</button><button data-t="3">Área 3D</button><button id="zmPlay" title="Aproximar do Brasil até a área">▶</button></div>'''
js='''<script>(function(){const KF=%s,svg=document.getElementById('zmap'),W=300,H=281;let t=3,goal=3,anim=null;
const lerp=(a,b,f)=>a+(b-a)*f,sm=f=>f*f*(3-2*f);
function view(t){const i=Math.min(2,Math.floor(t)),f=sm(t-i),A=KF[i],B=KF[i+1];const cx=lerp(A[0],B[0],f),cy=lerp(A[1],B[1],f),w=Math.exp(lerp(Math.log(A[2]),Math.log(B[2]),f)),h=w*H/W;
 svg.setAttribute('viewBox',`${cx-w/2} ${cy-h/2} ${w} ${h}`);const u=w/W;
 svg.querySelectorAll('.lb').forEach(e=>{const a=+e.dataset.a,b=+e.dataset.b,o=Math.max(0,Math.min(1,(t-a+.25)/.25,(b-t+.25)/.25));e.style.opacity=o;e.setAttribute('font-size',e.dataset.fs*u);e.style.strokeWidth=(3*u)+'px';});
 svg.querySelectorAll('.pe').forEach(e=>e.style.fillOpacity=Math.max(.15,Math.min(1,1-(t-1)*.85)));
 svg.querySelectorAll('.z1').forEach(e=>e.style.opacity=Math.max(0,Math.min(1,(t-.6)/.5)));
 svg.querySelectorAll('.z2').forEach(e=>e.style.opacity=Math.max(0,Math.min(1,(t-1.6)/.5)));
 svg.querySelectorAll('.emb').forEach(e=>{const w=e.dataset.w*u,h=e.dataset.h*u,a=+e.dataset.a,b=+e.dataset.b;e.setAttribute('width',w);e.setAttribute('height',h);e.setAttribute('x',e.dataset.ax-w);e.setAttribute('y',+e.dataset.ay);e.style.opacity=Math.max(0,Math.min(1,(t-a+.25)/.25,(b-t+.25)/.25));});
 svg.querySelectorAll('.sc').forEach(e=>e.setAttribute('r',e.dataset.r*u));
 const d=document.getElementById('zmDot'),p=document.getElementById('zmPulse');d.setAttribute('r',4*u);d.style.opacity=t<1.8?1:0;
 p.setAttribute('r',(7+5*Math.sin(performance.now()/300))*u);p.style.opacity=t<1.8?.8:0;
 document.querySelectorAll('.zmc button[data-t]').forEach(b=>b.classList.toggle('on',Math.abs(+b.dataset.t-t)<.5));}
let last=performance.now();function loop(now){const dt=Math.min(0.1,(now-last)/1000);last=now;const d=goal-t;if(Math.abs(d)>0.001){t+=Math.sign(d)*Math.min(Math.abs(d),dt*Math.max(0.9,Math.abs(d)*1.4));}else t=goal;view(t);requestAnimationFrame(loop);}
document.querySelectorAll('.zmc button[data-t]').forEach(b=>b.onclick=()=>{goal=+b.dataset.t;});
document.getElementById('zmPlay').onclick=()=>{t=0;goal=3;};
svg.addEventListener('wheel',e=>{e.preventDefault();goal=Math.max(0,Math.min(3,goal+(e.deltaY<0?0.25:-0.25)));},{passive:false});
t=0;goal=0;view(0);requestAnimationFrame(loop);setTimeout(()=>{goal=3;},1500);})();</script>'''%json.dumps(kf)
open('zoommap.html','w').write(svg+ctrl+js)
print(len(svg)//1024,'KB')
