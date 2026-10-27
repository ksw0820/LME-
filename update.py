import json, os, urllib.request, datetime, xml.etree.ElementTree as ET, re
from pathlib import Path
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).parent; DATA=ROOT/'data'/'market.json'
TODAY=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'CopperMarketDashboard/1.0 (+public market research)','Accept':'application/json, application/xml, text/xml, */*'})
 with urllib.request.urlopen(req,timeout=22) as r:return r.read()
def existing():
 try:return json.loads(DATA.read_text(encoding='utf-8'))
 except:return {'fx_history':[],'copper_history':[],'news':[]}
def get_fx():
 raw=json.loads(fetch('https://api.frankfurter.dev/v2/rates?base=USD&quotes=KRW'))
 if isinstance(raw,list):
  rows=[r for r in raw if r.get('quote')=='KRW'];r=rows[0];return {'date':r['date'],'value':float(r['rate']),'source':'Frankfurter (central bank reference)','url':'https://frankfurter.dev/'}
 return {'date':raw['date'],'value':float(raw['rates']['KRW']),'source':'Frankfurter','url':'https://frankfurter.dev/'}
def news():
 queries=['copper metal price supply demand','LME copper China economy','USD KRW exchange rate dollar']
 items=[]
 for q in queries:
  try:
   url='https://www.google.com/search?'+__import__('urllib.parse',fromlist=['urlencode']).urlencode({'q':q,'tbm':'nws'})
   # News headlines via Google News RSS (no scraping article text)
   rss='https://news.google.com/rss/search?'+__import__('urllib.parse',fromlist=['quote']).urlencode({'q':q,'hl':'en','gl':'US','ceid':'US:en'})
   root=ET.fromstring(fetch(rss))
   for item in root.findall('./channel/item')[:5]:
    title=item.findtext('title','').strip();link=item.findtext('link','').strip();date=item.findtext('pubDate','')
    if title and link and not any(x['title']==title for x in items):items.append({'title':title,'url':link,'published':date,'topic':q})
  except Exception as e:print('News warning:',e)
 return items[:12]
def main():
 d=existing();d['last_checked_kst']=TODAY; errors=[]
 try:
  fx=get_fx();d['fx']=fx
  h={x['date']:x for x in d.get('fx_history',[])};h[fx['date']]={'date':fx['date'],'value':fx['value']};d['fx_history']=sorted(h.values(),key=lambda x:x['date'])[-365:]
 except Exception as e:errors.append('환율 업데이트 실패: '+str(e))
 try:
  items=news()
  if items:d['news']=items
  else:errors.append('뉴스 조회 결과 없음')
 except Exception as e:errors.append('뉴스 업데이트 실패: '+str(e))
 # Official LME cash data cannot be redistributed without checking applicable license.
 # Instead copper is populated ONLY from an explicitly configured licensed JSON endpoint.
 endpoint=os.environ.get('COPPER_JSON_URL','').strip()
 if endpoint:
  try:
   c=json.loads(fetch(endpoint));date=c['date'];value=float(c['usd_per_tonne']);source=c['source'];source_url=c['source_url']
   if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',date) or not (1000<value<100000):raise ValueError('invalid copper date/value')
   d['copper']={'date':date,'value':value,'source':source,'url':source_url,'basis':c.get('basis','LME cash (verify contract)')}
   h={x['date']:x for x in d.get('copper_history',[])};h[date]={'date':date,'value':value};d['copper_history']=sorted(h.values(),key=lambda x:x['date'])[-365:]
  except Exception as e:errors.append('동 시세 연결 실패: '+str(e))
 else:errors.append('LME 정식 가격 데이터 공급원 미연결 — COPPER_JSON_URL 설정 필요')
 d['errors']=errors;DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Updated',TODAY,'errors:',errors)
if __name__=='__main__':main()
