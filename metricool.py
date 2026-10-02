from __future__ import annotations
import os, requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

BASE='https://app.metricool.com/api'


def headers():
    token=os.environ['METRICOOL_TOKEN']
    return {'X-Mc-Auth':token,'Content-Type':'application/json'}


def schedule_post(text, publication_dt, media_url=None, providers=('instagram','tiktok','youtube')):
    user_id=os.environ['METRICOOL_USER_ID']
    blog_id=os.environ['METRICOOL_BLOG_ID']
    creator=os.getenv('METRICOOL_CREATOR_EMAIL','')
    auto=os.getenv('METRICOOL_AUTO_PUBLISH','false').lower()=='true'
    body={
      'publicationDate': {'dateTime': publication_dt.strftime('%Y-%m-%dT%H:%M:%S'), 'timezone':'America/Sao_Paulo'},
      'text': text,
      'providers': [{'network':p} for p in providers],
      'autoPublish': auto,
      'draft': False,
      'shortener': False,
      'saveExternalMediaFiles': bool(media_url),
      'creatorUserMail': creator,
    }
    if media_url: body['media']=[media_url]
    url=f'{BASE}/v2/scheduler/posts'
    r=requests.post(url,params={'blogId':blog_id,'userId':user_id},headers=headers(),json=body,timeout=60)
    r.raise_for_status()
    return r.json()
