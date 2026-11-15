# Análise de preditores para a conversão MDS → MDT

3ª VE · Ciência de Dados Geográficos · IME
1º Ten Irineu · Aluno Baraúna · Orientadores: Cel Leonardo Moreira e Maj Diego · Colaborador: Ten João Inácio

Avaliação de dados candidatos, além dos 6 preditores do FathomDEM (Uhe et al., 2025), para reduzir o erro da conversão do Copernicus GLO-30 (MDS) em terreno (MDT). Teste em Guabiraba e Dois Irmãos, Recife, com o MDT LiDAR do PE3D (quadrícula SB-25-Y-C-VI-3-SO-E-IV) agregado para 30 m.

## Resultados parciais

| Configuração | Erro médio absoluto |
|---|---|
| Copernicus sem correção | 5,25 m |
| 6 preditores de referência | 2,59 m |
| Referência + 8 candidatos | 1,99 m (23% menor) |

Ganho de cada candidato isolado: GEM-15 menos Copernicus 0,21 m · Dossel Meta/WRI 0,20 m · Hansen 2000 0,16 m · ALOS PALSAR-2 0,14 m · HEM 0,08 m · Declividade 0,07 m · MapBiomas 0,07 m · GEM-15 rugosidade 0,06 m.

## Conteúdo

| Pasta | Arquivos |
|---|---|
| `01_Apresentacao` | Apresentação em HTML (setas mudam de slide, F = tela cheia) e em PDF |
| `02_Visualizacao_3D` | Página 3D interativa: liga e desliga preditores e mostra o erro em cada célula |
| `03_Scripts` | `analise.py` (troca e adição), `combos.py` (256 combinações), `seeds.py`, `build3d.py` e auxiliares |
| `04_Resultados` | `combinacoes_256.csv`, `res.json`, `toggles.json` |
| `05_Dados` | 22 camadas de preditores em 30 m (GeoTIFF) e dados OSM do mapa de localização |

Os arquivos HTML abrem direto no navegador (Chrome ou Edge), sem instalação. A extração das camadas foi feita no Google Earth Engine pelo servidor geeflow.

## Referências

- Uhe, P. et al. (2025). FathomDEM: an improved global terrain map using a hybrid vision transformer model. *Environmental Research Letters* 20, 034002.
- Nunes, J. I. A. Encoder Comparison for FathomDEM-based DSM-to-DTM Correction in Northeastern Brazil. IME.
