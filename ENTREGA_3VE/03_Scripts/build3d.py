# =====================================================================
# build3d.py — montador da página 3D
# Junta relevo LiDAR (3 m), altura das árvores, ortofoto, os erros das 256
# combinações, os mapas dos preditores, bairros/vias e o mapa de localização
# num único HTML que funciona sem internet:
#   02_Visualizacao_3D/erro_MDS_3D_DoisIrmaos.html
# Uso: python3 build3d.py <ortofoto.png>
# =====================================================================
import json, numpy as np, base64
W='/home/claude/work/'
b64=lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
C=np.load(W+'combos.npz'); preds=C['preds']; y=C['y']; mask=C['mask']
TOG=json.load(open(W+'toggles.json'))
M=np.load(W+'maps.npz'); dem=np.load(W+'dem5.npz')
res=json.load(open(W+'res.json'))
H,Wd=80,118
idx=np.flatnonzero(mask.ravel())
R=y[None,:]-preds  # residuals
step=0.2
Rq=np.clip(np.round(R/step),-127,127).astype(np.int8)
mae=np.abs(R).mean(axis=1)
best=int(np.argmin(mae))
zoff=20.0
d3=np.load(W+'dem3.npz'); t3=np.round((d3['t3']-zoff)*100).astype(np.uint16); nd=np.round(d3['nd']*4).astype(np.uint8)
import io, sys
from PIL import Image
SATSRC=sys.argv[1] if len(sys.argv)>1 else 's2'
import rasterio
names=['cop_dsm','cop_hem','cop_wbm','cop_edm','slope','s1_vh','eth_ch','lc100_tree','ghs_bh','meta_ch','ob_height','ob_presence','hansen_tc2000','hansen_lossyear','mapbiomas_2015','palsar_hh','palsar_hv','jrc_occ','gem_dsm','gem_std','gem_p95_p5','gem_dtm']
P={n:a.astype('float32') for n,a in zip(names,rasterio.open(W+'preds.tif').read())}
for n in P: P[n][~np.isfinite(P[n])]=np.nan
P['gem_minus_cop']=P['gem_dsm']-P['cop_dsm']; P['mb_forest']=(P['mapbiomas_2015']==3).astype('float32')
lay=[('dh','Erro do Copernicus','m',M['dh']),('ch','Altura do dossel/objetos (LiDAR)','m',M['ch']),('cop_dsm','Copernicus GLO-30 (MDS)','m',P['cop_dsm']),
 ('cop_hem','HEM do Copernicus','m',P['cop_hem']),('eth_ch','Dossel ETH 2020','m',P['eth_ch']),('meta_ch','Dossel Meta/WRI','m',P['meta_ch']),
 ('palsar_hv','ALOS PALSAR-2 HV (banda L)','dB',P['palsar_hv']),('gem_minus_cop','GEM-15 menos Copernicus','m',P['gem_minus_cop']),
 ('gem_std','GEM-15 rugosidade (desvio)','m',P['gem_std']),('hansen_tc2000','Hansen cobertura 2000','%',P['hansen_tc2000']),
 ('mb_forest','MapBiomas floresta (2015)','0/1',P['mb_forest']),('slope','Declividade','°',P['slope']),('s1_vh','Sentinel-1 VH','dB',P['s1_vh'])]
layers={}
for k,n,u,a in lay:
    a=np.asarray(a,dtype='float32'); v=a[np.isfinite(a)]
    r=[float(np.percentile(v,2)),float(np.percentile(v,98))] if k!='mb_forest' else [0,1]
    layers[k]={'name':n,'u':u,'r':[round(r[0],2),round(r[1],2)],'d':b64(np.where(np.isfinite(a),a,np.nan).astype('float32'))}
import rasterio as rio
S2=rio.open('/mnt/user-data/uploads/CDG -TRABALHO/analise_preditores/s2_rgb_5m_v2.tif').read().astype('float32')
for k in range(3):
    lo,hi=np.percentile(S2[k],1),np.percentile(S2[k],99); S2[k]=np.clip((S2[k]-lo)/(hi-lo),0,1)**0.85*255
sat=np.ascontiguousarray(S2.transpose(1,2,0)).astype(np.uint8)
if SATSRC=='s2':
    im=Image.fromarray(sat).resize((1416,960),Image.BICUBIC); satname='imagem Sentinel-2 em cor real (2019–2022, 10 m)'
else:
    im=Image.open(SATSRC).convert('RGB'); satname='ortoimagem PE3D (0,5 m, reamostrada para ~0,9 m)'
buf=io.BytesIO(); im.save(buf,'JPEG',quality=80,optimize=True); satjpg=base64.b64encode(buf.getvalue()).decode()
ov=json.load(open('/home/claude/ctx/overlays.json'))
data={'satjpg':satjpg,'ov':ov,'W3':int(t3.shape[1]),'H3':int(t3.shape[0]),'t3':b64(t3),'nd':b64(nd),'W':Wd,'H':H,'zoff':zoff,
 'idx':idx.tolist(),'res':b64(Rq),'rstep':step,'mae':[round(float(m),4) for m in mae],'best':best,
 'toggles':TOG,'layers':layers,'bias':float(res['bias_open']),'meraw':float(res['raw']['me'])}
html=open('/home/claude/site/t3d2.html',encoding='utf-8').read().replace('/*__INSET__*/',open('/home/claude/ctx/inset.svg').read()).replace('/*__HELP__*/',open('/home/claude/site/help.js',encoding='utf-8').read()).replace('/*__SATNAME__*/',satname[0].upper()+satname[1:] if False else satname)
three=open('/home/claude/npm3/node_modules/three/build/three.min.js',encoding='utf-8').read()
orbit=open('/home/claude/npm3/node_modules/three/examples/js/controls/OrbitControls.js',encoding='utf-8').read()
html=html.replace('/*__THREE__*/',three.replace('</script','<\\/script')).replace('/*__ORBIT__*/',orbit).replace('/*__DATA__*/null',json.dumps(data,separators=(',',':')))
open('/home/claude/site/3d/index.html','w',encoding='utf-8').write(html)
print('size MB',len(html)/1e6,'base',mae[0],'best',best,mae[best],'all',mae[-1], [TOG[i][1] for i in range(len(TOG)) if best>>i&1])
