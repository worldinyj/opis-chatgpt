import copy, tempfile, unittest, wave, math, struct
from pathlib import Path
from PIL import Image
import media_v2 as m

FONT='/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
def fixture(ratio='16:9'):
    w,h=(320,180) if ratio=='16:9' else (180,320)
    def scene(id,route):
        return dict(id=id,duration_seconds=1,overlap_to_next_seconds=0,title='테스트',scene_type='FACT',fact_ids=['F01'],learning_ids=[],overlay=['테스트'],narration='',visual_brief='synthetic',render_mode='STILL_MOTION',generation_route=route,reference_ids=[],input_mode=None,motion_plan=dict(start_scale=1,end_scale=1.12,pan='NONE'))
    return dict(schema_version='2.0',event_id='TEST',artifact_id='TEST-01',revision=1,title='테스트',profile=dict(width=w,height=h,fps=24,aspect_ratio=ratio,style='synthetic'),timing=dict(target_seconds=2),scenes=[scene('S01','GEMINI_TASKS_BATCH'),scene('S02','INDIVIDUAL')],references=[])
class Test(unittest.TestCase):
    def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name); self.m=fixture()
    def tearDown(self): self.tmp.cleanup()
    def test_timeline(self):
        self.assertEqual(m.timeline(self.m)[1]['start'],1)
        self.m['scenes'][0]['overlap_to_next_seconds']=.25; self.m['timing']['target_seconds']=1.75
        self.assertEqual(m.timeline(self.m)[1]['start'],.75)
    def test_invalid_timeline(self):
        self.m['scenes'][0]['overlap_to_next_seconds']=1
        with self.assertRaises(ValueError): m.timeline(self.m)
    def test_build(self):
        m.build(self.m,self.root); self.assertIn('[NOT WRITTEN]',(self.root/'NARRATION.md').read_text()); self.assertTrue((self.root/'IMAGE_PROMPTS.md').exists())
    def test_batch(self):
        b=m.batch_export(self.m,self.root,self.root); self.assertEqual(len(b['jobs']),1)
        self.assertIsNone(m.batch_import(b,self.m,self.root)['results'][0]['sha256'])
        p=self.root/b['jobs'][0]['expected_filename']; Image.new('RGB',(320,180)).save(p)
        r=m.batch_import(b,self.m,self.root)['results'][0]; self.assertEqual(r['result'],'PENDING'); self.assertEqual(r['sha256'],m.digest(p))
        Image.new('RGB',(180,320)).save(p); self.assertEqual(m.batch_import(b,self.m,self.root)['results'][0]['result'],'REJECTED')
    def test_stale_batch(self):
        b=m.batch_export(self.m,self.root,self.root); b['manifest_revision']=99
        with self.assertRaises(ValueError): m.batch_import(b,self.m,self.root)
    def test_path_escape(self):
        b=m.batch_export(self.m,self.root,self.root); b['jobs'][0]['expected_filename']='../x.png'
        with self.assertRaises(ValueError): m.batch_import(b,self.m,self.root)
    def test_voice_overrun(self):
        with wave.open(str(self.root/'S01.wav'),'wb') as w: w.setparams((1,2,8000,0,'NONE','not compressed')); w.writeframes(b'\0\0'*9000)
        with self.assertRaises(ValueError): m.voice_plan(self.m,self.root)
    def test_render_and_assemble(self):
        for ratio in ('16:9','9:16'):
            x=fixture(ratio); p=x['profile']; w,h=p['width'],p['height']; image=self.root/'test.png'; Image.new('RGB',(w,h),'#345678').save(image)
            for i,s in enumerate(x['scenes']):
                motion=dict(start_scale=1,end_scale=1.12,pan='NONE') if i==0 else dict(start_scale=1.12,end_scale=1,pan='LEFT')
                result=m.render_still(image,self.root/(s['id']+'.mp4'),p,1,motion); self.assertEqual(result['width'],w)
            with wave.open(str(self.root/'S01.wav'),'wb') as a: a.setparams((1,2,8000,0,'NONE','not compressed')); a.writeframes(b''.join(struct.pack('<h',int(1000*math.sin(i*.1))) for i in range(4000)))
            result=m.assemble(x,self.root,self.root,self.root/'out.mp4'); self.assertEqual(result['seconds'],2); self.assertTrue(any(s['codec_type']=='audio' for s in m.probe(self.root/'out.mp4')['streams']))
    def test_card(self):
        for ratio in ('16:9','9:16'):
            p=fixture(ratio)['profile']; p.update(width=p['width']*4,height=p['height']*4)
            groups=[('WP',['WP1 작업 관리','WP3 문서화','WP4 절차 준수']),('CO',['CO1 업무 소통']),('QA',['QA2 불확실성 확인','QA4 자만 방지']),('DM',['DM1 일관적 프로세스','DM2 보수적 성향']),('PI',['PI1 문제 파악','PI2 문제 평가','PI3 문제 해결']),('CL',['CL1 운전 경험'])]
            f=self.root/'card.png'; m.card(f,p,'원칙별 미진속성 후보',groups,FONT); self.assertEqual(Image.open(f).size,(p['width'],p['height']))
if __name__=='__main__': unittest.main(verbosity=2)
