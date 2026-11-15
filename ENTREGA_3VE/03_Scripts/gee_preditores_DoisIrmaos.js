// =====================================================================
// Análise de preditores para a conversão MDS -> MDT · 3ª VE · IME
// Extração das 22 camadas usadas no trabalho (Google Earth Engine, Code Editor)
// Área: Guabiraba e Dois Irmãos, Recife (quadrícula PE3D SB-25-Y-C-VI-3-SO-E-IV)
// Grade: EPSG:31985 (SIRGAS 2000 / UTM 25S), 30 m
// Como usar: cole em https://code.earthengine.google.com e clique em Run.
// =====================================================================

// ---------- Área de estudo (mesma extensão do arquivo preditores_SB25YCVI3SOEIV_30m.tif)
var CRS = 'EPSG:31985';
var aoi = ee.Geometry.Rectangle([282942.848473, 9115154.033807, 286482.848473, 9117554.033807],
                                CRS, false);

// ---------- 1. Copernicus GLO-30 (MDS, HEM, máscara d'água, EDM) e declividade
var copCol = ee.ImageCollection('COPERNICUS/DEM/GLO30').filterBounds(aoi);
var copProj = copCol.first().select('DEM').projection();
var cop = copCol.mosaic().setDefaultProjection(copProj);
var cop_dsm = cop.select('DEM').rename('cop_dsm');
var cop_hem = cop.select('HEM').rename('cop_hem');
var cop_wbm = cop.select('WBM').rename('cop_wbm');
var cop_edm = cop.select('EDM').rename('cop_edm');
var slope   = ee.Terrain.slope(cop_dsm).rename('slope');

// ---------- 2. Sentinel-1 VH (mediana 2016-2017, modo IW)
var s1_vh = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(aoi).filterDate('2016-01-01', '2018-01-01')
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH'))
  .select('VH').median().rename('s1_vh');

// ---------- 3. Altura do dossel ETH 2020 (10 m)
var eth_ch = ee.Image('users/nlang/ETH_GlobalCanopyHeight_2020_10m_v1').rename('eth_ch');

// ---------- 4. Fração arbórea Copernicus LC100 (2015)
var lc100_tree = ee.Image('COPERNICUS/Landcover/100m/Proba-V-C3/Global/2015')
  .select('tree-coverfraction').rename('lc100_tree');

// ---------- 5. Altura de edificações GHS-BUILT-H 2018 (substituto do WSF3D)
var ghs_bh = ee.Image('JRC/GHSL/P2023A/GHS_BUILT_H/2018').select('built_height').rename('ghs_bh');

// ---------- 6. Candidato: dossel Meta/WRI (1 m)
var meta_ch = ee.ImageCollection('projects/meta-forest-monitoring-okw37/assets/CanopyHeight')
  .filterBounds(aoi).mosaic().select('cover_code').rename('meta_ch');

// ---------- 7. Candidato: Open Buildings 2.5D (altura e presença de edificações)
var ob = ee.ImageCollection('GOOGLE/Research/open-buildings-temporal/v1')
  .filterBounds(aoi).filterDate('2016-01-01', '2024-01-01').mosaic();
var ob_height   = ob.select('building_height').rename('ob_height');
var ob_presence = ob.select('building_presence').rename('ob_presence');

// ---------- 8. Candidato: Hansen Global Forest Change (cobertura 2000 e ano de perda)
var hansen = ee.Image('UMD/hansen/global_forest_change_2024_v1_12');
var hansen_tc2000   = hansen.select('treecover2000').rename('hansen_tc2000');
var hansen_lossyear = hansen.select('lossyear').unmask(0).rename('hansen_lossyear');

// ---------- 9. Candidato: MapBiomas Coleção 10 (2015). Floresta = classe 3
var mapbiomas_2015 = ee.Image(
  'projects/mapbiomas-public/assets/brazil/lulc/collection10/mapbiomas_brazil_collection10_integration_v2')
  .select('classification_2015').rename('mapbiomas_2015');

// ---------- 10. Candidato: ALOS PALSAR-2 (banda L, mosaico anual 2015, em dB)
var palsar = ee.ImageCollection('JAXA/ALOS/PALSAR/YEARLY/SAR_EPOCH')
  .filterDate('2015-01-01', '2016-01-01').filterBounds(aoi).mosaic();
var toDb = function (dn) { return dn.pow(2).log10().multiply(10).subtract(83); };
var palsar_hh = toDb(palsar.select('HH').toFloat()).rename('palsar_hh');
var palsar_hv = toDb(palsar.select('HV').toFloat()).rename('palsar_hv');

// ---------- 11. Água superficial JRC (ocorrência)
var jrc_occ = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('occurrence').unmask(0).rename('jrc_occ');

// ---------- 12. Candidato: GEM-15 (MDS óptico do Google, 15 m, experimental)
var gem = ee.ImageCollection('projects/climate-and-sustainability/assets/gem-15_v1')
  .filterBounds(aoi).mosaic();
var gem_dsm    = gem.select('dsm').rename('gem_dsm');
var gem_std    = gem.select('dsm_std').rename('gem_std');
var gem_p95_p5 = gem.select('dsm_percentile_95').subtract(gem.select('dsm_percentile_5')).rename('gem_p95_p5');
var gem_dtm    = gem.select('dtm').rename('gem_dtm');

// ---------- Pilha das 22 camadas, na mesma ordem do GeoTIFF do trabalho
var stack = ee.Image.cat([
  cop_dsm, cop_hem, cop_wbm, cop_edm, slope, s1_vh, eth_ch, lc100_tree, ghs_bh,
  meta_ch, ob_height, ob_presence, hansen_tc2000, hansen_lossyear, mapbiomas_2015,
  palsar_hh, palsar_hv, jrc_occ, gem_dsm, gem_std, gem_p95_p5, gem_dtm
]).toFloat().clip(aoi);
print('Bandas (22):', stack.bandNames());

// Variáveis derivadas usadas na análise
var mb_forest     = mapbiomas_2015.eq(3).rename('mb_forest');
var gem_minus_cop = gem_dsm.subtract(cop_dsm).rename('gem_minus_cop');

// ---------- Visualização no mapa
Map.centerObject(aoi, 15);
Map.setOptions('SATELLITE');
var green = ['ffffff', 'c7e9c0', '74c476', '238b45', '00441b'];
Map.addLayer(cop_dsm.clip(aoi), {min: 0, max: 120, palette: ['0b3d91', '2e7d32', 'f9a825', 'ffffff']}, 'MDS Copernicus', false);
Map.addLayer(cop_hem.clip(aoi), {min: 0, max: 2, palette: ['ffffff', 'ef6c00']}, 'HEM do Copernicus', false);
Map.addLayer(slope.clip(aoi), {min: 0, max: 30, palette: ['ffffff', '5d4037']}, 'Declividade', false);
Map.addLayer(s1_vh.clip(aoi), {min: -22, max: -8}, 'Sentinel-1 VH', false);
Map.addLayer(eth_ch.clip(aoi), {min: 0, max: 30, palette: green}, 'Dossel ETH', true);
Map.addLayer(meta_ch.clip(aoi), {min: 0, max: 30, palette: green}, 'Dossel Meta/WRI', false);
Map.addLayer(hansen_tc2000.clip(aoi), {min: 0, max: 100, palette: green}, 'Hansen cobertura 2000', false);
Map.addLayer(mb_forest.selfMask().clip(aoi), {palette: ['1f8d49']}, 'MapBiomas floresta 2015', false);
Map.addLayer(palsar_hv.clip(aoi), {min: -25, max: -10}, 'ALOS PALSAR-2 HV (dB)', false);
Map.addLayer(gem_minus_cop.clip(aoi), {min: -15, max: 15, palette: ['2166ac', 'f7f7f7', 'b2182b']}, 'GEM-15 menos Copernicus', false);
Map.addLayer(gem_std.clip(aoi), {min: 0, max: 5, palette: ['ffffff', '6a1b9a']}, 'GEM-15 rugosidade', false);
Map.addLayer(ee.Image().paint(aoi, 0, 3), {palette: ['ffeb3b']}, 'Área de estudo');

// ---------- Exportação (opcional): descomente para gerar o GeoTIFF no Google Drive
// Export.image.toDrive({image: stack, description: 'preditores_SB25YCVI3SOEIV_30m',
//   region: aoi, crs: CRS, crsTransform: [30, 0, 282942.848473, 0, -30, 9117554.033807],
//   maxPixels: 1e9});
