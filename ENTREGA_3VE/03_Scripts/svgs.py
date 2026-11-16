# =====================================================================
# svgs.py — diagramas das caixas de ajuda (parte 1)
# Desenha os esquemas que aparecem ao passar o mouse na página 3D:
# radar e penetração na copa, GEM-15, MDS × MDT e rugosidade. Saída: svgs.json
# =====================================================================
import json
def crowns(xs,y,r,col='#2f7d4f',dark='#256b42'):
    return ''.join(f'<circle cx="{x}" cy="{y+(i%2)*6}" r="{r}" fill="{col if i%2 else dark}"/>' for i,x in enumerate(xs))
def trunks(xs,y0,y1): return ''.join(f'<rect x="{x-3}" y="{y0}" width="6" height="{y1-y0}" fill="#6b4a2b"/>' for x in xs)
def arrow(x,y0,y1,c): return f'<line x1="{x}" y1="{y0}" x2="{x}" y2="{y1-6}" stroke="{c}" stroke-width="3"/><path d="M{x-5} {y1-7} L{x+5} {y1-7} L{x} {y1} Z" fill="{c}"/><circle cx="{x}" cy="{y1+2}" r="3.5" fill="none" stroke="{c}" stroke-width="1.5"/>'
T='font-family="system-ui,Segoe UI,sans-serif"'
# radar
cx=[30,55,80,105,130,155,180,205,230,255]
radar=f'''<svg viewBox="0 0 280 160" {T}><rect width="280" height="160" fill="#15181a"/>
{trunks([55,130,205],80,128)}{crowns(cx,58,17)}
<rect x="0" y="128" width="280" height="6" fill="#c8a477"/>
<g font-size="10" fill="#f0efec" text-anchor="middle"><text x="40" y="13" font-weight="600">Banda X</text><text x="40" y="24" fill="#9a998f">Copernicus</text>
<text x="107" y="13" font-weight="600">Banda C</text><text x="107" y="24" fill="#9a998f">Sentinel-1</text>
<text x="174" y="13" font-weight="600">Banda L</text><text x="174" y="24" fill="#9a998f">PALSAR</text>
<text x="241" y="13" font-weight="600">Banda P</text><text x="241" y="24" fill="#9a998f">BIOMASS</text></g>
{arrow(40,30,42,'#f2c14e')}{arrow(107,30,56,'#9ec5f4')}{arrow(174,30,92,'#f4a582')}{arrow(241,30,126,'#e66767')}
<text x="140" y="152" font-size="10" fill="#b9b8b0" text-anchor="middle">Onda mais longa = o sinal chega mais fundo</text></svg>'''
# gem
cx2=[35,62,89,116,143,170,197,224,251]
gem=f'''<svg viewBox="0 0 280 150" {T}><rect width="280" height="150" fill="#15181a"/>
{trunks([62,143,224],72,112)}{crowns(cx2,54,17)}
<rect x="0" y="112" width="280" height="6" fill="#c8a477"/>
<path d="M14 40 Q62 31 89 35 Q116 31 143 35 Q170 31 197 35 Q224 31 266 38" stroke="#ffffff" stroke-width="2.5" fill="none"/>
<path d="M14 54 Q62 46 89 50 Q116 46 143 50 Q170 46 197 50 Q224 46 266 52" stroke="#f2c14e" stroke-width="2.5" fill="none" stroke-dasharray="6 4"/>
<line x1="262" y1="38" x2="262" y2="52" stroke="#e66767" stroke-width="2"/><line x1="257" y1="38" x2="267" y2="38" stroke="#e66767" stroke-width="2"/><line x1="257" y1="52" x2="267" y2="52" stroke="#e66767" stroke-width="2"/>
<text x="266" y="22" font-size="10.5" fill="#e66767" text-anchor="end" font-weight="600">diferença = preditor</text>
<g font-size="10.5" fill="#d8d7d0"><line x1="12" y1="133" x2="34" y2="133" stroke="#fff" stroke-width="2.5"/><text x="40" y="137">GEM-15: topo da copa</text>
<line x1="172" y1="133" x2="194" y2="133" stroke="#f2c14e" stroke-width="2.5" stroke-dasharray="6 4"/><text x="200" y="137">Copernicus</text></g></svg>'''
# mds x mdt
mds=f'''<svg viewBox="0 0 280 150" {T}><rect width="280" height="150" fill="#15181a"/>
{trunks([45,85,125],70,104)}{crowns([30,52,74,96,118,140],52,16)}
<rect x="190" y="62" width="44" height="44" fill="#8a8a86"/><rect x="198" y="70" width="8" height="8" fill="#5c5c58"/><rect x="216" y="70" width="8" height="8" fill="#5c5c58"/><rect x="198" y="86" width="8" height="8" fill="#5c5c58"/><rect x="216" y="86" width="8" height="8" fill="#5c5c58"/>
<path d="M0 108 Q70 100 140 106 T280 102" stroke="#c8a477" stroke-width="4" fill="none"/>
<path d="M4 44 Q30 32 60 34 Q100 30 150 40 L175 96 L188 62 L236 62 L250 100 L276 100" stroke="#f2c14e" stroke-width="2.5" fill="none" stroke-dasharray="6 4"/>
<line x1="96" y1="34" x2="96" y2="102" stroke="#e66767" stroke-width="2"/><line x1="91" y1="34" x2="101" y2="34" stroke="#e66767" stroke-width="2"/><line x1="91" y1="102" x2="101" y2="102" stroke="#e66767" stroke-width="2"/>
<text x="102" y="22" font-size="10.5" fill="#e66767" font-weight="600">erro = MDS − chão</text>
<g font-size="10.5" fill="#d8d7d0"><line x1="12" y1="133" x2="34" y2="133" stroke="#f2c14e" stroke-width="2.5" stroke-dasharray="6 4"/><text x="40" y="137">MDS (topo)</text>
<line x1="140" y1="133" x2="162" y2="133" stroke="#c8a477" stroke-width="4"/><text x="168" y="137">MDT (chão real)</text></g></svg>'''
# rug
rug=f'''<svg viewBox="0 0 280 96" {T}><rect width="280" height="96" fill="#15181a"/>
<rect x="14" y="44" width="110" height="4" fill="#9ec5f4"/>
<path d="M150 50 l7 -16 l6 12 l7 -22 l7 20 l6 -14 l8 18 l7 -26 l7 22 l6 -12 l8 16 l7 -20 l8 22 l6 -10 l6 10" stroke="#3fc48f" stroke-width="2.5" fill="none"/>
<g font-size="10.5" fill="#d8d7d0" text-anchor="middle"><text x="69" y="74" font-weight="600">Liso</text><text x="69" y="87" fill="#9a998f">telhado, pasto, água</text>
<text x="208" y="74" font-weight="600">Áspero</text><text x="208" y="87" fill="#9a998f">mata</text></g></svg>'''
d={'radar':radar,'gem':gem,'mdsmdt':mds,'rug':rug}
json.dump(d,open('svgs.json','w'))
open('preview.html','w').write('<body style="background:#000;margin:0;display:grid;grid-template-columns:300px 300px;gap:10px;padding:10px">'+''.join(f'<div style="width:300px">{v}</div>' for v in d.values())+'</body>')
