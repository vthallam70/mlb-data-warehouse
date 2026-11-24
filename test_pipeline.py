import sqlite3, unittest
from pipeline import dates,load
class PipelineTest(unittest.TestCase):
 def test_backfill_and_idempotency(self):
  self.assertEqual(list(dates('2024-04-01','2024-04-02')),['2024-04-01','2024-04-02'])
  db=sqlite3.connect(':memory:'); p={'dates':[{'date':'2024-04-01','games':[{'gamePk':1,'teams':{'home':{'team':{'name':'A'}},'away':{'team':{'name':'B'}}}}]}]}
  load(db,p); load(db,p); self.assertEqual(db.execute('select count(*) from games').fetchone()[0],1)
