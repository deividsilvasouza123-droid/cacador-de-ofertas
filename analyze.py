from __future__ import annotations
import csv, json
from pathlib import Path
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'data'/'desempenho.csv'
OUT=ROOT/'output'/'metricas'/'recomendacoes.json'


def num(v):
    try: return float(v or 0)
    except: return 0.0


def rate(rows, metric, denom='views'):
    v=sum(num(r[metric]) for r in rows); d=sum(num(r[denom]) for r in rows)
    return (v/d*100) if d else 0


def group(rows, key):
    d=defaultdict(list)
    for r in rows: d[r.get(key,'(sem dado)')].append(r)
    return d

with SRC.open(encoding='utf-8-sig', newline='') as f:
    rows=list(csv.DictReader(f))

result={'rows':len(rows),'top_hooks':[],'top_angles':[],'top_networks':[],'rules':[]}
for label,key in [('top_hooks','hook'),('top_angles','angle'),('top_networks','network')]:
    stats=[]
    for k,rs in group(rows,key).items():
        if not k or k=='(sem dado)': continue
        stats.append({'value':k,'views':sum(num(x['views']) for x in rs),'click_rate':round(rate(rs,'outbound_clicks'),3),'share_rate':round(rate(rs,'shares'),3),'save_rate':round(rate(rs,'saves'),3),'rows':len(rs)})
    stats.sort(key=lambda x:(x['click_rate'],x['views']), reverse=True)
    result[label]=stats[:10]

if rows:
    result['rules'].append('Gerar mais variações dos hooks com maior taxa de clique.')
    result['rules'].append('Não abandonar um hook só por poucas visualizações: exigir amostra mínima antes de decidir.')
    result['rules'].append('Separar desempenho por rede, porque o mesmo criativo pode reagir de forma diferente.')
else:
    result['rules'].append('Ainda não há dados. Começar com testes A/B e alimentar data/desempenho.csv.')

OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
