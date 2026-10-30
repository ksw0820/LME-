import json, os, urllib.request, datetime, xml.etree.ElementTree as ET, re
from pathlib import Path
from urllib.parse import urlencode
ROOT=Path(__file__).parent
DATA=ROOT/'data'/'market.json'
NOW=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(timespec='seconds')
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'MetalPulse/2.0 (market dashboard)','Accept':'application/json, application/xml, text/xml, */*'})
 with urllib.request.urlopen(req,timeout=25) as r:return r.read()
def load():
 try:return json.loads(DATA.read_text(encoding='utf-8'))
 except:return {}
def validate_date(s):
 datetime.date.fromisoformat(s)
 if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',s):raise ValueError('invalid date')
def add(history,date,value):
 h={x['date']:x for x in history if isinstance(x,dict) and 'date' in x and 'value' in x}
 h[date]={'date':date,'value':value}
 return sorted(h.values(),key=lambda x:x['date'])[-1100:]
def endpoint_price(url,lo,hi,expected_basis=None):
 p=json.loads(fetch(url));date=p['date'];validate_date(date)
 v=float(p.get('usd_per_tonne',p.get('value')))
 if not lo<v<hi:raise ValueError('price out of range')
 if not p.get('source') or not p.get('source_url'):raise ValueError('source and source_url required')
 if expected_basis and p.get('basis')!='LME Official Cash Seller & Settlement':raise ValueError('basis must explicitly be LME Official Cash Seller & Settlement')
 return {'date':date,'value':v,'source':p['source'],'url':p['source_url'],'basis':p.get('basis',expected_basis or 'USD/KRW 최초고시 매매기준율')}
def news():
 out=[]
 for q in ['LME copper zinc tin supply demand','China industrial economy copper demand','USD KRW Federal Reserve interest rates']:
  try:
   root=ET.fromstring(fetch('https://news.google.com/rss/search?'+urlencode({'q':q,'hl':'en','gl':'US','ceid':'US:en'})))
   for item in root.findall('./channel/item')[:5]:
    t=item.findtext('title','').strip();u=item.findtext('link','').strip()
    if t and u and not any(x['title']==t for x in out):out.append({'title':t,'url':u,'published':item.findtext('pubDate',''),'topic':q})
  except Exception as e:print('News warning:',e)
 return out[:12]
def main():
 d=load();d['last_checked_kst']=NOW;errors=[]
 metals=d.get('metals',{});history=d.get('metal_history',{})
 # Backward-compatible migration of historical copper values only, never invent prices.
 if d.get('copper') and 'cu' not in metals:metals['cu']=d['copper']
 if d.get('copper_history') and 'cu' not in history:history['cu']=d['copper_history']
 for code,name,lo,hi in [('cu','동',1000,100000),('zn','아연',500,20000),('sn','주석',1000,150000)]:
  url=os.environ.get('LME_'+code.upper()+'_JSON_URL','').strip()
  if not url:errors.append(name+' Cash 공식 가격 공급원 미연결');continue
  try:
   p=endpoint_price(url,lo,hi,True);metals[code]=p;history[code]=add(history.get(code,[]),p['date'],p['value'])
  except Exception as e:errors.append(name+' 수집 실패: '+str(e))
 d['metals']=metals;d['metal_history']=history
 fxurl=os.environ.get('HANA_FX_JSON_URL','').strip()
 if fxurl:
  try:
   p=endpoint_price(fxurl,100,5000)
   if p.get('basis')!='하나은행 USD/KRW 1회차 매매기준율':raise ValueError('basis must explicitly be 하나은행 USD/KRW 1회차 매매기준율')
   d['hana_fx']=p;d['hana_fx_history']=add(d.get('hana_fx_history',[]),p['date'],p['value'])
  except Exception as e:errors.append('최초고시환율 수집 실패: '+str(e))
 else:errors.append('하나은행 최초고시환율 공급원 미연결')
 # Old Frankfurter reference FX must never be presented as Hana first quotation.
 try:
  n=news()
  if n:d['news']=n
  else:errors.append('뉴스 신규 수집 결과 없음')
 except Exception as e:errors.append('뉴스 조회 실패: '+str(e))
 d['errors']=errors;DATA.parent.mkdir(exist_ok=True);DATA.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Updated',NOW,'warnings:',errors)
if __name__=='__main__':main()
