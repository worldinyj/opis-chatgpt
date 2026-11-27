"""Full F1 runtime archive backup/restore; requires pinned Git contract loader."""
import sqlite3
import tempfile
import unittest
from pathlib import Path
import test_f1f2 as fixtures
import c09_f1_intake as intake
import c09_f2_snapshot as snapshot
import c02_r2 as core
from c09_connection import reopen
from c09_archive_audit import verify
from c04_r1_bridge import calculate


def audit(db):
    db.execute('BEGIN')
    try:return verify(db)
    finally:db.rollback()


class Restore(unittest.TestCase):
    def test_complete_restore(self):
        db=intake.connect(fixtures.STANDARD)
        try:
            intake.baseline(db,fixtures.baseline())
            for i in range(900,938):
                for m in ('GEMINI','CLAUDE'):
                    self.assertEqual(intake.ingest(db,*fixtures.packet(i,m),fixtures.SCHEMA,fixtures.STANDARD),'STAGED_NOT_ELIGIBLE')
            self.assertEqual(intake.ingest(db,*fixtures.packet(900,'GEMINI',role='I'),fixtures.SCHEMA,fixtures.STANDARD),'CONFLICT_QUARANTINED')
            sid,_=snapshot.seal(db);calculate(db,sid)
            expected=dict(archives=78,staged=77,conflicts=1,bindings=114,artifacts=381,approved=False,can_ship=False)
            self.assertEqual(audit(db),expected);fp=core.digest(db,sid)
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/'restore.sqlite';dest=sqlite3.connect(path)
                try:db.backup(dest)
                finally:dest.close()
                restored=reopen(path)
                try:
                    self.assertEqual(audit(restored),expected)
                    self.assertEqual(core.digest(restored,sid),fp)
                    self.assertEqual(calculate(restored,sid),('NOOP',1520))
                    self.assertEqual(restored.execute('SELECT * FROM consensus ORDER BY key').fetchall(),db.execute('SELECT * FROM consensus ORDER BY key').fetchall())
                    self.assertEqual(restored.execute('SELECT count(*) FROM ai_review').fetchone(),(4560,))
                    self.assertEqual(restored.execute('SELECT count(*) FROM eligibility').fetchone(),(0,))
                finally:restored.close()
        finally:db.close()

if __name__=='__main__':unittest.main(verbosity=2)
