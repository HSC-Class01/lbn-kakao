import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from agent import number,extract,enrich,classify,candidates_from_zip
import io,zipfile
class TestAgent(unittest.TestCase):
 def test_number(self):
  self.assertEqual(number('(1,234)'),-1234);self.assertIsNone(number('-'));self.assertIsNone(number('1억원'))
 def test_ytd(self):
  rows=[dict(sj_div='IS',account_id='ifrs-full_Revenue',account_nm='매출액',thstrm_amount='30',thstrm_add_amount='90',currency='KRW')]
  v,q,t,w=extract(rows,'11014');self.assertEqual(v['revenue'],90);self.assertEqual(q['revenue'],30)
 def test_ambiguous(self):
  rows=[dict(sj_div='BS',account_id='ifrs-full_Assets',thstrm_amount=str(n)) for n in [1,2]]
  v,q,t,w=extract(rows,'11011');self.assertIsNone(v['assets']);self.assertTrue(w)
 def test_revenue_excludes_gross_profit_alias(self):
  rows=[dict(sj_div='CIS',account_id='ifrs-full_GrossProfit',account_nm='영업수익',thstrm_amount='100',currency='KRW')]
  v,q,t,w=extract(rows,'11011');self.assertIsNone(v['revenue']);self.assertTrue(any('excluded mismatched' in x for x in w))
 def test_revenue_accepts_unstandardized_alias(self):
  rows=[dict(sj_div='CIS',account_id='-표준계정코드 미사용-',account_nm='영업수익',thstrm_amount='100',currency='KRW')]
  v,q,t,w=extract(rows,'11011');self.assertEqual(v['revenue'],100)
 def test_segment_cash_reconciles(self):
  rows=[
   dict(sj_div='BS',account_id='-표준계정코드 미사용-',account_nm='현금및현금성자산, 금융업',thstrm_amount='10',currency='KRW'),
   dict(sj_div='BS',account_id='-표준계정코드 미사용-',account_nm='현금및현금성자산, 비금융업',thstrm_amount='90',currency='KRW'),
   dict(sj_div='CF',account_id='dart_CashAndCashEquivalentsAtEndOfPeriodCf',account_nm='기말현금및현금성자산',thstrm_amount='100',currency='KRW')]
  v,q,t,w=extract(rows,'11011');self.assertEqual(v['cash'],100);self.assertEqual(t['cash']['source'],'segment_sum_reconciled_to_cash_flow');self.assertFalse(any('cash: conflicting' in x for x in w))
 def test_missing_ytd(self):
  v,*_=extract([dict(sj_div='IS',account_id='ifrs-full_Revenue',thstrm_amount='10')],'11012');self.assertIsNone(v['revenue'])
 def test_ratios(self):
  rs=[dict(year=y,reprt_code='11011',fs_div='CFS',values=dict(revenue=rev,operating_profit=20,net_income=10,assets=a,equity=e,liabilities=40,current_assets=30,current_liabilities=15)) for y,rev,a,e in [(2023,100,100,50),(2024,120,120,60)]]
  enrich(rs);self.assertAlmostEqual(rs[1]['ratios']['revenue_yoy'],20);self.assertAlmostEqual(rs[1]['ratios']['roa'],10/110*100);self.assertAlmostEqual(rs[1]['ratios']['roe'],10/55*100)
 def test_classify(self):
  self.assertEqual(classify({'report_nm':'[기재정정]사업보고서 (2010.12)'}),(2010,'11011'))
  self.assertIsNone(classify({'report_nm':'주요사항보고서 (2024.12)'}))
 def test_legacy(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:z.writestr('old.xml','<table><tr><td>자산총계</td><td>100</td></tr></table>')
  r=candidates_from_zip(b.getvalue(),'123');self.assertEqual(r[0]['status'],'REVIEW_REQUIRED')
if __name__=='__main__':unittest.main()
