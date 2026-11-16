# =====================================================================
# analise.py — 1º passo da análise (Random Forest)
# Lê as 22 camadas (05_Dados/preditores_...tif) e o MDT LiDAR do PE3D em 30 m,
# calcula o alvo Δh = MDS Copernicus − MDT LiDAR e testa os preditores:
#   • modelo base (preditores do FathomDEM);
#   • TROCA de um preditor por um candidato (ex.: Meta no lugar do ETH);
#   • ADIÇÃO de cada candidato ao modelo base;
#   • correlação de cada camada com o erro, erro por altura do dossel e viés em área aberta.
# Validação cruzada em blocos espaciais (GroupKFold). Saída: 04_Resultados/res.json
# =====================================================================
import rasterio, numpy as np, json, warnings
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold
warnings.filterwarnings('ignore')
names=['cop_dsm','cop_hem','cop_wbm','cop_edm','slope','s1_vh','eth_ch','lc100_tree','ghs_bh','meta_ch','ob_height','ob_presence','hansen_tc2000','hansen_lossyear','mapbiomas_2015','palsar_hh','palsar_hv','jrc_occ','gem_dsm','gem_std','gem_p95_p5','gem_dtm']
P={n:a.astype('float64') for n,a in zip(names,rasterio.open('preds.tif').read())}
for n in P: P[n][~np.isfinite(P[n])]=np.nan
P['hansen_lossyear']=np.nan_to_num(P['hansen_lossyear'],nan=0)
L=np.load('lidar30.npz')
H,W=80,118
dh=P['cop_dsm']-L['mdt']
P['mb_forest']=(P['mapbiomas_2015']==3).astype(float)
P['loss_pos2010']=(P['hansen_lossyear']>=11).astype(float)
P['gem_minus_cop']=P['gem_dsm']-P['cop_dsm']
open_px=L['ch_p95']<2
bias_open=float(np.nanmedian(dh[open_px])) if open_px.sum()>20 else float('nan')
ch=L['ch_p95']
mask=np.isfinite(dh)&np.isfinite(P['eth_ch'])&np.isfinite(P['cop_hem'])
print('pixels',mask.sum(),'open px',open_px.sum(),'bias open',bias_open)
y=dh[mask]
rr,cc=np.indices((H,W)); groups=((rr//16)*100+(cc//20))[mask]
def X(feats): return np.column_stack([P[f][mask] for f in feats])
def cv(feats,seed=0):
    pred=np.zeros_like(y)
    for tr,te in GroupKFold(5).split(y,y,groups):
        m=RandomForestRegressor(300,min_samples_leaf=3,n_jobs=-1,random_state=seed).fit(X(feats)[tr],y[tr]); pred[te]=m.predict(X(feats)[te])
    return pred
BASE=['cop_dsm','s1_vh','eth_ch','ghs_bh','lc100_tree']
res={}
pb=cv(BASE); rb=y-pb
def mae(r): return float(np.mean(np.abs(r)))
res['raw']={'mae':mae(y-np.median(y)),'me':float(np.mean(y))}
res['base']={'mae':mae(rb),'rmse':float(np.sqrt(np.mean(rb**2)))}
exps={
 'HEM do Copernicus':BASE+['cop_hem'],
 'Dossel Meta no lugar do ETH':[f if f!='eth_ch' else 'meta_ch' for f in BASE],
 'Open Buildings no lugar do GHS':[f if f!='ghs_bh' else 'ob_height' for f in BASE],
 'MapBiomas no lugar do LC100':[f if f!='lc100_tree' else 'mb_forest' for f in BASE],
 'ALOS PALSAR-2 (HH, HV)':BASE+['palsar_hh','palsar_hv'],
 'GEM-15 rugosidade':BASE+['gem_std','gem_p95_p5'],
 'GEM-15 menos Copernicus':BASE+['gem_minus_cop'],
 'Hansen perda pos-2010':BASE+['loss_pos2010'],
 'Declividade':BASE+['slope'],
 'Hansen cobertura 2000':BASE+['hansen_tc2000'],
}
for k,f in exps.items():
    r=y-cv(f); res[k]={'mae':mae(r),'delta_pct':100*(mae(r)-res['base']['mae'])/res['base']['mae']}
    print(f"{k:32s} MAE {res[k]['mae']:.3f}  {res[k]['delta_pct']:+.1f}%")
# combined best
best=[k for k in exps if res[k]['delta_pct']<-1]
print('best',best)
comb=set(BASE)
for k in best: comb|=set(exps[k])
# resolve swaps: if swap improved, drop old
if 'Dossel Meta no lugar do ETH' in best: comb.discard('eth_ch')
if 'Open Buildings no lugar do GHS' in best: comb.discard('ghs_bh')
if 'MapBiomas no lugar do LC100' in best: comb.discard('lc100_tree')
comb=sorted(comb); pc=cv(comb); rc=y-pc
res['combo']={'feats':comb,'mae':mae(rc),'rmse':float(np.sqrt(np.mean(rc**2))),'delta_pct':100*(mae(rc)-res['base']['mae'])/res['base']['mae']}
print('combo',res['combo'])
# correlations with dh
corr={}
for f in ['cop_hem','eth_ch','meta_ch','ghs_bh','ob_height','lc100_tree','mb_forest','hansen_tc2000','palsar_hh','palsar_hv','gem_std','gem_p95_p5','gem_minus_cop','slope','s1_vh','loss_pos2010']:
    v=P[f][mask]; corr[f]=float(spearmanr(v,y).correlation) if np.nanstd(v)>0 else None
res['spearman']=corr
# canopy maps vs lidar canopy
chm=ch[mask]
res['canopy_check']={k:{'spearman':float(spearmanr(P[k][mask],chm).correlation),'mae':float(np.mean(np.abs(P[k][mask]-chm)))} for k in ['eth_ch','meta_ch']}
# strata
bins=[(0,5),(5,10),(10,20),(20,99)]
st=[]
for lo,hi in bins:
    s=(chm>=lo)&(chm<hi)
    st.append({'faixa':f'{lo}-{hi if hi<99 else ""}','n':int(s.sum()),'raw':mae((y-bias_open)[s]),'base':mae(rb[s]),'combo':mae(rc[s])})
res['strata']=st; res['n']=int(mask.sum()); res['bias_open']=bias_open
print(json.dumps({k:res[k] for k in ['raw','base','spearman','canopy_check','strata']},indent=0))
full=lambda r: (lambda a:(a.__setitem__(mask,r),a)[1])(np.full((H,W),np.nan))
np.savez('maps.npz',dh=dh,res_base=full(rb),res_combo=full(rc),ch=ch,mdt=L['mdt'],**{k:P[k] for k in ['cop_dsm','cop_hem','eth_ch','meta_ch','ob_height','ghs_bh','palsar_hv','gem_std','mb_forest','slope']})
json.dump(res,open('res.json','w'),indent=1)
