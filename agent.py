"""DART ingestion: raw archives, audited metric selection and static publication."""
import argparse, csv, io, json, os, re, time, zipfile
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent
BASE='https://opendart.fss.or.kr/api/'
CODES={3:'11013',6:'11012',9:'11014',12:'11011'}
METRICS=json.loads((ROOT/'metrics.json').read_text(encoding='utf-8'))
def load(p,default):
 q=ROOT/p
 return json.loads(q.read_text(encoding='utf-8')) if q.exists() else default

def save(p,data):
 q=ROOT/p;q.parent.mkdir(parents=True,exist_ok=True)
 tmp=q.with_suffix(q.suffix+'.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');tmp.replace(q)

def number(v):
 if v is None:return None
 s=str(v).strip().replace(',','').replace(' ','').replace('−','-')
 if s in ('','-','—'):return None
 if s.startswith('(') and s.endswith(')'):s='-'+s[1:-1]
 return int(s) if re.fullmatch(r'-?\d+',s) else None

def norm(v):return re.sub(r'\s+','',v or '')

class Dart:
 def __init__(self,key):self.key=key;self.session=requests.Session()
 def request(self,endpoint,**params):
  # Do not log request URLs: they contain the API secret.
  for attempt in range(5):
   try:
    r=self.session.get(BASE+endpoint,params={'crtfc_key':self.key,**params},timeout=(15,120))
    if r.status_code==429 or r.status_code>=500:
     time.sleep(2**attempt);continue
    if r.status_code!=200:raise RuntimeError(f'DART HTTP {r.status_code}')
    time.sleep(.25);return r
   except (requests.Timeout,requests.ConnectionError):time.sleep(2**attempt)
  raise RuntimeError('DART network retry limit reached')
 def js(self,endpoint,**params):
  for attempt in range(4):
   d=self.request(endpoint,**params).json();status=d.get('status')
   if status=='000':return d
   if status=='013':return {'list':[],'total_page':0,'status':'013'}
   if status in ('800','900'):time.sleep(2**attempt);continue
   raise RuntimeError(f'DART status {status}; check official error guide')
  raise RuntimeError('DART service temporarily unavailable')
 def binary(self,endpoint,**params):
  b=self.request(endpoint,**params).content
  if not zipfile.is_zipfile(io.BytesIO(b)):
   try:status=ET.fromstring(b).findtext('status')
   except ET.ParseError:status='invalid binary'
   raise RuntimeError(f'DART archive error {status}')
  return b
 def corp(self):
  b=self.binary('corpCode.xml')
  with zipfile.ZipFile(io.BytesIO(b)) as z:
   root=ET.fromstring(z.read('CORPCODE.xml'))
  hits=[e for e in root.findall('list') if (e.findtext('stock_code') or '').strip()=='035720']
  if len(hits)!=1:raise RuntimeError('KAKAO stock-code resolution ambiguous')
  return hits[0].findtext('corp_code')

def classify(report):
 name=report['report_nm']; m=re.search(r'\((\d{4})\.(\d{2})\)',name)
 if not m:return None
 y,month=map(int,m.groups())
 if '사업보고서' in name and month==12:code='11011'
 elif '반기보고서' in name and month==6:code='11012'
 elif '분기보고서' in name and month in (3,9):code=CODES[month]
 else:return None
 if y<2010:return None
 return y,code

def candidates_from_zip(b,rcept):
 # Candidate tables only: never guess current-period column, units or CFS/OFS.
 results=[]
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  for name in z.namelist():
   if not name.lower().endswith(('.xml','.html','.htm')):continue
   raw=z.read(name)
   try:text=raw.decode('utf-8-sig')
   except UnicodeDecodeError:text=raw.decode('cp949',errors='replace')
   soup=BeautifulSoup(text,'html.parser')
   for n,t in enumerate(soup.find_all('table')):
    txt=t.get_text(' ',strip=True)
    if not any(w in txt for w in ('자산총계','매출액','영업수익','영업이익','영업활동')):continue
    prev=t.find_previous(['title','p','div'])
    results.append({'rcept_no':rcept,'file':name,'table_index':n,'context':prev.get_text(' ',strip=True)[-1000:] if prev else '',
      'rows':[[c.get_text(' ',strip=True) for c in row.find_all(['td','th','te'])] for row in t.find_all('tr')],
      'status':'REVIEW_REQUIRED','text':txt[:25000]})
 return results

def extract(rows,code):
 vals={};trace={};quarter={}; warnings=[]
 for metric,cfg in METRICS.items():
  sj=['IS','CIS'] if cfg['statement']=='IS' else [cfg['statement']]
  eligible=[r for r in rows if r.get('sj_div') in sj and r.get('currency','KRW')=='KRW']
  hits=[r for r in eligible if r.get('account_id') in cfg['ids']]
  if not hits:hits=[r for r in eligible if norm(r.get('account_nm')) in [norm(x) for x in cfg['names']]]
  # IS preferred to identical CIS repeat. Conflicting duplicates stay missing.
  if any(r.get('sj_div')=='IS' for r in hits):hits=[r for r in hits if r.get('sj_div')=='IS']
  field='thstrm_add_amount' if cfg['statement']=='IS' and code!='11011' else 'thstrm_amount'
  values={number(r.get(field)) for r in hits};values.discard(None)
  vals[metric]=next(iter(values)) if len(values)==1 else None
  if len(values)>1:warnings.append(metric+': conflicting accounts')
  if vals[metric] is not None:
   chosen=next(r for r in hits if number(r.get(field))==vals[metric])
   trace[metric]={'account_id':chosen.get('account_id'),'account_nm':chosen.get('account_nm'),'field':field,'rcept_no':chosen.get('rcept_no')}
  if cfg['statement']=='IS' and code!='11011':
   q={number(r.get('thstrm_amount')) for r in hits};q.discard(None)
   quarter[metric]=next(iter(q)) if len(q)==1 else None
 return vals,quarter,trace,warnings

def ratio(a,b):return a/b*100 if a is not None and b is not None and b>0 else None

def enrich(records):
 index={(r['year'],r['reprt_code'],r['fs_div']):r for r in records}
 for r in records:
  v=r['values'];p=index.get((r['year']-1,r['reprt_code'],r['fs_div']))
  prev=p['values'] if p else {}
  growth=lambda k: (v[k]/prev[k]-1)*100 if v.get(k) is not None and prev.get(k) is not None and prev[k]>0 else None
  r['ratios']={'operating_margin':ratio(v.get('operating_profit'),v.get('revenue')),'net_margin':ratio(v.get('net_income'),v.get('revenue')),
   'debt_ratio':ratio(v.get('liabilities'),v.get('equity')),'current_ratio':ratio(v.get('current_assets'),v.get('current_liabilities')),
   'equity_ratio':ratio(v.get('equity'),v.get('assets')),'revenue_yoy':growth('revenue'),'operating_profit_yoy':growth('operating_profit')}
  # ROA/ROE: annual only, average year-end assets/equity, total NI/total equity.
  py=index.get((r['year']-1,'11011',r['fs_div']))
  for label,denom in [('roa','assets'),('roe','equity')]:
   a=v.get(denom);b=py['values'].get(denom) if py else None
   r['ratios'][label]=ratio(v.get('net_income'),(a+b)/2) if r['reprt_code']=='11011' and a is not None and b is not None else None
 return records

def apply_overrides(records):
 idx={(r['year'],r['reprt_code'],r['fs_div']):r for r in records}
 with (ROOT/'overrides.csv').open(encoding='utf-8-sig',newline='') as f:
  for row in csv.DictReader(f):
   if row['reviewed'].lower()!='true':continue
   key=(int(row['year']),row['reprt_code'],row['fs_div']);metric=row['metric']
   if key not in idx or metric not in METRICS:raise ValueError('Override period or metric not found')
   r=idx[key]
   if row['rcept_no']!=r['rcept_no']:raise ValueError('Override stale: receipt differs from latest report')
   if not row['source_note'].strip():raise ValueError('Override needs source note and unit/period evidence')
   val=number(row['value_krw'])
   if val is None:raise ValueError('Override amount must be integer KRW')
   r['values'][metric]=val;r['trace'][metric]={'source':'reviewed_override','rcept_no':row['rcept_no'],'note':row['source_note']}
   r['status']='reviewed_partial' if any(x is None for x in r['values'].values()) else 'reviewed'
 return records

def collect(full=False):
 key=os.environ.get('DART_API_KEY','').strip()
 if not re.fullmatch(r'[a-zA-Z0-9]{40}',key):raise RuntimeError('Set DART_API_KEY: 40-character API key')
 dart=Dart(key);corp=dart.corp();today=datetime.now(ZoneInfo('Asia/Seoul')).date()
 reports={r['rcept_no']:r for r in load('data/reports.json',[])}
 # Re-scan all filing years: catches corrections to old reporting periods.
 for year in range(2010,today.year+1):
  end=min(today,datetime(year,12,31).date()).strftime('%Y%m%d');page=1
  while True:
   d=dart.js('list.json',corp_code=corp,bgn_de=f'{year}0101',end_de=end,pblntf_ty='A',last_reprt_at='N',page_count=100,page_no=page)
   for r in d.get('list',[]):
    if classify(r):reports[r['rcept_no']]=r
   if page>=int(d.get('total_page',0)):break
   page+=1
 latest={}
 for r in reports.values():
  period=classify(r)
  if not period or '철' in r.get('rm',''):continue
  if period not in latest or r['rcept_no']>latest[period]['rcept_no']:latest[period]=r
 # Persist all originals/corrections, not only the selected latest report.
 for receipt,r in sorted(reports.items()):
  p=ROOT/f'data/raw/reports/{receipt}.zip'
  if not p.exists():
   b=dart.binary('document.xml',rcept_no=receipt);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
  if classify(r)[0]<2015:
   out=ROOT/f'data/legacy_candidates/{receipt}.json'
   if not out.exists():save(str(out.relative_to(ROOT)),candidates_from_zip(p.read_bytes(),receipt))
 save('data/reports.json',sorted(reports.values(),key=lambda x:x['rcept_no']))
 records=[]
 for (year,code),r in sorted(latest.items()):
  for fs in ('CFS','OFS'):
   cache=f'data/raw/financials/{year}_{code}_{fs}.json'
   if year>=2015:
    # Refresh every period, so historical restatements are not missed.
    d=dart.js('fnlttSinglAcntAll.json',corp_code=corp,bsns_year=year,reprt_code=code,fs_div=fs);save(cache,d)
    rows=d.get('list',[])
    vals,q,tr,w=extract(rows,code)
    receipts=sorted({x.get('rcept_no') for x in rows if x.get('rcept_no')})
    if receipts and receipts!=[r['rcept_no']]:w.append('API financial receipt differs from selected filing; check trace')
    status='api' if rows else 'api_unavailable'
   else:vals={k:None for k in METRICS};q={};tr={};w=['2010–2014: original tables require reviewed override'];status='legacy_review_required'
   records.append({'year':year,'reprt_code':code,'fs_div':fs,'category':'annual' if code=='11011' else 'Half-year' if code=='11012' else 'quarterly',
    'period':f"{year} { {'11011':'FY','11012':'H1','11013':'Q1','11014':'Q3'}[code]}",'rcept_no':r['rcept_no'],'report_name':r['report_nm'],
    'url':'https://dart.fss.or.kr/dsaf001/main.do?rcpNo='+r['rcept_no'],'values':vals,'quarter_values':q,'trace':tr,'warnings':w,'status':status})
 records=enrich(apply_overrides(records));save('data/financials.json',records)
 save('data/status.json',{'updated_at':datetime.now(timezone.utc).isoformat(),'corp_code':corp,'stock_code':'035720','reports':len(reports),'periods':len(latest),'records':len(records),'legacy_review_required':sum(r['status']=='legacy_review_required' for r in records)})

def build():
 records=load('data/financials.json',[])
 if not (ROOT/'data/financials.json').exists():save('data/financials.json',records)
 if not (ROOT/'data/reports.json').exists():save('data/reports.json',[])
 peers=load('peers.json',[]);status=load('data/status.json',{'updated_at':None})
 template=(ROOT/'template.html').read_text(encoding='utf-8')
 payload=json.dumps({'records':records,'peers':peers,'status':status},ensure_ascii=False,allow_nan=False).replace('<','\\u003c')
 html=template.replace('__PAYLOAD__',payload)
 (ROOT/'docs').mkdir(exist_ok=True);(ROOT/'docs/index.html').write_text(html,encoding='utf-8')
 (ROOT/'docs/dashboard-badge.svg').write_text((ROOT/'dashboard-badge.svg').read_text(encoding='utf-8'),encoding='utf-8')

def main():
 p=argparse.ArgumentParser();p.add_argument('--build-only',action='store_true');p.add_argument('--full',action='store_true');a=p.parse_args()
 if not a.build_only:collect(a.full)
 build()
if __name__=='__main__':main()
