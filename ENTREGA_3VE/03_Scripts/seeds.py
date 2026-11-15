exec(open('analise.py').read().split("res={}")[0])
import json
BASE=['cop_dsm','s1_vh','eth_ch','ghs_bh','lc100_tree']
exps={'base':BASE,
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
 'combo':json.load(open('res.json'))['combo']['feats']}
out={k:[] for k in exps}
for s in [1,2]:
  for k,f in exps.items(): out[k].append(float(np.mean(np.abs(y-cv(f,seed=s)))))
json.dump(out,open('seeds.json','w'),indent=1); print(out)
