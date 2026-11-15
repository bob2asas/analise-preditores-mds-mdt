exec(open('analise.py').read().split("res={}")[0])
import itertools, json, time
from sklearn.ensemble import HistGradientBoostingRegressor
from joblib import Parallel, delayed
BASE=['cop_dsm','s1_vh','eth_ch','ghs_bh','lc100_tree']
TOG=[('hem','HEM do Copernicus',['cop_hem']),('palsar','ALOS PALSAR-2 (banda L)',['palsar_hh','palsar_hv']),
 ('gemdiff','GEM-15 menos Copernicus',['gem_minus_cop']),('gemrug','GEM-15 rugosidade',['gem_std','gem_p95_p5']),
 ('hansen','Hansen cobertura 2000',['hansen_tc2000']),('slope','Declividade',['slope']),
 ('mapbiomas','MapBiomas floresta',['mb_forest']),('meta','Dossel Meta/WRI',['meta_ch'])]
folds=list(GroupKFold(5).split(y,y,groups))
def run(mask_bits):
    feats=BASE+[f for i,t in enumerate(TOG) if mask_bits>>i&1 for f in t[2]]
    Xa=X(feats); pred=np.zeros_like(y)
    for tr,te in folds:
        m=HistGradientBoostingRegressor(max_iter=300,learning_rate=0.06,max_leaf_nodes=31,min_samples_leaf=20,random_state=0).fit(Xa[tr],y[tr]); pred[te]=m.predict(Xa[te])
    return mask_bits, pred
t=time.time()
out=Parallel(n_jobs=-1)(delayed(run)(b) for b in range(2**len(TOG)))
print('time',time.time()-t)
preds=np.zeros((2**len(TOG),y.size),dtype='float32')
for b,p in out: preds[b]=p
np.savez('combos.npz',preds=preds,y=y.astype('float32'),mask=mask)
json.dump([[t[0],t[1]] for t in TOG],open('toggles.json','w'))
r=[float(np.mean(np.abs(y-preds[b]))) for b in range(256)]
print('base',r[0],'all',r[255],'best',min(r),int(np.argmin(r)))
