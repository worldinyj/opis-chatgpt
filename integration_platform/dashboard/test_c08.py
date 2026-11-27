import unittest
from c08_dashboard import render, fixture, table

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.html=render(*fixture())
    def test_counts(self):
        for s in ('1,520개 검토키','4,560개 슬롯','1,040개','<strong>520</strong>','<strong>480</strong>'):self.assertIn(s,self.html)
    def test_groups(self):
        for s in ('principle','attribute','plant','year','event'):self.assertIn('id="'+s+'"',self.html)
    def test_labels(self):
        for s in ('SYNTHETIC ONLY','공통 완전사례','쌍별 적격','미산정','approved=false','can_ship=false'):self.assertIn(s,self.html)
    def test_escape(self): self.assertNotIn('<script>',table(['<script>'],[['<script>']]))
    def test_real(self):
        e,b,m=fixture();m[e[0]]['plant']='REAL';self.assertRaises(ValueError,render,e,b,m)
    def test_missing(self):
        e,b,m=fixture();b.pop(next(iter(b)));self.assertRaises(ValueError,render,e,b,m)
    def test_no_remote(self):
        self.assertNotIn('<script',self.html);self.assertNotIn('https://',self.html)
if __name__=='__main__':unittest.main(verbosity=2)
