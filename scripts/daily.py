from __future__ import annotations
import json, os, re
from pathlib import Path
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from engine import main as generate
from metricool import schedule_post

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'roteiros'
TZ=ZoneInfo('America/Sao_Paulo')

# 1) Gera lote de roteiros.
generate()

# 2) Agenda apenas quando o Metricool estiver configurado.
required=['METRICOOL_TOKEN','METRICOOL_USER_ID','METRICOOL_BLOG_ID']
if not all(os.getenv(k) for k in required):
    print('Metricool não configurado; lote de roteiros criado e nada foi publicado/agendado.')
    raise SystemExit(0)

latest=json.loads((OUT/'latest_batch.json').read_text(encoding='utf-8'))
media_tpl=os.getenv('MEDIA_URL_TEMPLATE','').strip()
now=datetime.now(TZ)
# horários iniciais baseados nos testes já observados na conta: 10h, 12h, 18h.
slots=[time(10,0),time(12,0),time(18,0)]
for i,item in enumerate(latest[:3]):
    slot=slots[i]
    dt=datetime.combine((now+timedelta(days=1)).date(),slot,tzinfo=TZ)
    script=item['scripts'][i % len(item['scripts'])]
    name=item['product_name']
    link=item['offer_link']
    caption=f"{script['hook']}\n\n{name[:120]}\n\nConfere o preço no link 👇\n{link}\n\n#achadinhos #shopee #ofertas #utilidades #promoções"
    media_url=media_tpl.format(item_id=item['product_id']) if media_tpl else None
    result=schedule_post(caption,dt,media_url=media_url)
    print('Agendado:', item['product_id'], dt.isoformat(), result)
