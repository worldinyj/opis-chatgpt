"""Offline OPIS v2 builder. No network or paid generation."""
import argparse, hashlib, json, math, re, subprocess, wave
from pathlib import Path


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def save(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def safe(root, name):
    root = Path(root).resolve()
    p = (root / name).resolve()
    if not p.is_relative_to(root) or p == root:
        raise ValueError('unsafe path')
    return p


def timeline(m):
    if m['schema_version'] != '2.0':
        raise ValueError('v2 required')
    p = m['profile']
    w, h, fps = p['width'], p['height'], p['fps']
    if p['aspect_ratio'] not in ('9:16', '16:9') or min(w,h,fps) <= 0 or w%2 or h%2:
        raise ValueError('invalid profile')
    a,b = map(int,p['aspect_ratio'].split(':'))
    if abs(w/h-a/b) > .005:
        raise ValueError('ratio mismatch')
    scenes = m['scenes']; t = 0; rows = []; seen = set()
    for i,s in enumerate(scenes):
        sid = s['id']; d = s['duration_seconds']; o = s['overlap_to_next_seconds']
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',sid) or sid in seen:
            raise ValueError('invalid/duplicate scene ID')
        if not all(math.isfinite(x) for x in (d,o)) or d <= 0 or o < 0 or o >= d or (i==len(scenes)-1 and o) or (i+1<len(scenes) and o>=scenes[i+1]['duration_seconds']):
            raise ValueError('invalid duration/overlap')
        seen.add(sid); rows.append(dict(id=sid,start=round(t,6),end=round(t+d,6),duration=d,overlap=o)); t += d-o
    if not rows or abs(t-m['timing']['target_seconds']) > .001:
        raise ValueError('target mismatch')
    return rows


def build(m, out):
    out=Path(out); out.mkdir(parents=True,exist_ok=True)
    rows=timeline(m); save(out/'timeline.json',rows)
    lines=['# Storyboard — '+m['title'],'','PLANNING ONLY; no generation or approval.','']
    narr=['# Korean narration (draft)','']; images=['# Image prompts (draft)','']; videos=['# I2V prompts (draft)','']
    refs={r['id']:r for r in m['references']}
    for s,r in zip(m['scenes'],rows):
        label=f"{s['id']} | {r['start']:.3f}–{r['end']:.3f}s | {s['scene_type']}"
        lines += ['## '+label,s['title'],s['visual_brief'], 'F: '+', '.join(s['fact_ids'])+' / L: '+', '.join(s['learning_ids']), 'Overlay: '+' / '.join(s['overlay']),'']
        narr += ['## '+s['id'],s['narration'] or '[NOT WRITTEN]','']
        if s['render_mode']!='CONTROLLED_GRAPHIC':
            ref='; '.join(x+': '+refs[x]['description'] for x in s['reference_ids'])
            prompt=f"{m['profile']['style']}; {m['profile']['aspect_ratio']}; {s['visual_brief']}; references: {ref}; no generated text; conceptual education only."
            images += ['## '+s['id'],prompt,'']
            if s['render_mode']=='I2V':
                videos += ['## '+s['id'],prompt+f" Input: {s['input_mode']}; duration: {s['duration_seconds']}s; use approved reference images; one location and one main action.",'']
    for name,ls in [('STORYBOARD.md',lines),('NARRATION.md',narr),('IMAGE_PROMPTS.md',images),('I2V_PROMPTS.md',videos)]:
        (out/name).write_text('\n'.join(ls)+'\n',encoding='utf-8')
    return rows


def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)],text=True))


def check_video(path, profile, seconds):
    data=probe(path); v=next(s for s in data['streams'] if s['codec_type']=='video')
    n,d=map(float,v['avg_frame_rate'].split('/')); actual=float(data['format']['duration'])
    if (v['width'],v['height'])!=(profile['width'],profile['height']) or abs(n/d-profile['fps'])>.01 or abs(actual-seconds)>max(.06,1/profile['fps']+.01):
        raise ValueError('output media mismatch')
    return dict(width=v['width'],height=v['height'],fps=n/d,seconds=actual,sha256=digest(path))


def render_still(image, out, profile, seconds, motion):
    w,h,fps=profile['width'],profile['height'],profile['fps']; frames=round(seconds*fps)
    a,b=motion['start_scale'],motion['end_scale']
    if not (1<=a<=2 and 1<=b<=2 and frames>=2):
        raise ValueError('zoom range or duration')
    pan=motion['pan']; x={'NONE':'(iw-iw/zoom)/2','LEFT':'(iw-iw/zoom)*(1-on/%d)'%(frames-1),'RIGHT':'(iw-iw/zoom)*on/%d'%(frames-1),'UP':'(iw-iw/zoom)/2','DOWN':'(iw-iw/zoom)/2'}[pan]
    y={'UP':'(ih-ih/zoom)*(1-on/%d)'%(frames-1),'DOWN':'(ih-ih/zoom)*on/%d'%(frames-1)}.get(pan,'(ih-ih/zoom)/2')
    vf=f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},zoompan=z='{a}+({b}-{a})*on/{frames-1}':x='{x}':y='{y}':d={frames}:s={w}x{h}:fps={fps},format=yuv420p"
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(image),'-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-threads','2',str(out)],check=True)
    return check_video(out,profile,seconds)


def card(out, profile, title, groups, font_path):
    from PIL import Image, ImageDraw, ImageFont
    w,h=profile['width'],profile['height']; im=Image.new('RGB',(w,h),'#F3F6FA'); d=ImageDraw.Draw(im)
    cols=2 if w>h else 1; rows=math.ceil(len(groups)/cols); pad=round(w*.035); top=round(h*.15); gap=pad; cw=(w-2*pad-(cols-1)*gap)//cols; ch=(h-top-pad-(rows-1)*gap)//rows
    size=max(12,min(round(w*.028),ch//5)); f=ImageFont.truetype(str(font_path),size); bold=ImageFont.truetype(str(font_path),round(size*1.3)); tf=ImageFont.truetype(str(font_path),round(w*.037))
    if d.textlength(title,font=tf)>w-2*pad: raise ValueError('title does not fit')
    d.text((pad,pad),title,font=tf,fill='#17334C')
    for i,(name,items) in enumerate(groups):
        x=pad+(i%cols)*(cw+gap); y=top+(i//cols)*(ch+gap); d.rounded_rectangle((x,y,x+cw,y+ch),radius=8,fill='white'); lines=[(name,bold)]+[(v,f) for v in items]
        yy=y+8
        for text,font in lines:
            if d.textlength(text,font=font)>cw-16 or yy+font.size+4>y+ch: raise ValueError('card text does not fit')
            d.text((x+8,yy),text,font=font,fill='#17334C'); yy+=font.size+4
    im.save(out)


def voice_plan(m, audio_dir):
    result=[]
    for s,r in zip(m['scenes'],timeline(m)):
        path=safe(audio_dir,s['id']+'.wav')
        if not path.exists():
            if s['narration'].strip(): raise ValueError('missing narration '+s['id'])
            continue
        with wave.open(str(path)) as f: seconds=f.getnframes()/f.getframerate()
        if seconds > r['duration']-r['overlap']+.001: raise ValueError('narration overrun '+s['id'])
        result.append(dict(id=s['id'],start=r['start'],seconds=seconds,path=str(path),sha256=digest(path)))
    return result


def batch_export(m, root, out):
    timeline(m); out=Path(out); out.mkdir(parents=True,exist_ok=True); jobs=[]; refs={r['id']:r for r in m['references']}
    for s in m['scenes']:
        if s['generation_route']!='GEMINI_TASKS_BATCH': continue
        if s['render_mode']=='CONTROLLED_GRAPHIC': raise ValueError('graphic must be edited locally')
        for rid in s['reference_ids']:
            r=refs[rid]
            if r['review_status']!='PASS' or not r['path'] or not r['sha256'] or digest(safe(root,r['path']))!=r['sha256']: raise ValueError('unverified reference '+rid)
        kind='VIDEO' if s['render_mode']=='I2V' else 'IMAGE'; ext='.mp4' if kind=='VIDEO' else '.png'
        jobs.append(dict(id='J'+str(len(jobs)+1).zfill(2),scene_id=s['id'],requested_kind=kind,prompt=f"{m['profile']['style']}; {m['profile']['aspect_ratio']}; {s['visual_brief']}; no generated text; educational concept only.",reference_ids=s['reference_ids'],expected_filename=s['id']+'_take01'+ext,attempt=1))
    if not jobs: raise ValueError('no batch scenes')
    b=dict(schema_version='2.0',job_id=m['artifact_id']+'-R'+str(m['revision']),event_id=m['event_id'],artifact_id=m['artifact_id'],manifest_revision=m['revision'],route='GEMINI_TASKS_BATCH',aspect_ratio=m['profile']['aspect_ratio'],jobs=jobs,results=[])
    save(out/'batch_job.json',b); save(out/'reference_inventory.json',[refs[r] for r in sorted({r for j in jobs for r in j['reference_ids']})]); return b


def batch_import(b,m,root):
    if (b['event_id'],b['artifact_id'],b['manifest_revision'],b['aspect_ratio'])!=(m['event_id'],m['artifact_id'],m['revision'],m['profile']['aspect_ratio']): raise ValueError('stale batch')
    scenes={s['id']:s for s in m['scenes']}; seen=set(); results=[]
    for j in b['jobs']:
        if j['id'] in seen or j['scene_id'] not in scenes or scenes[j['scene_id']]['generation_route']!='GEMINI_TASKS_BATCH': raise ValueError('invalid job')
        seen.add(j['id']); p=safe(root,j['expected_filename']); status='PENDING'; note='Missing file'; sha=None; actual=None
        if p.is_file():
            try:
                if j['requested_kind']=='IMAGE':
                    from PIL import Image
                    with Image.open(p) as im: im.verify()
                    with Image.open(p) as im: w,h=im.size
                    a,c=map(int,b['aspect_ratio'].split(':'))
                    if abs(w/h-a/c)>.02: raise ValueError('wrong image ratio')
                elif j['requested_kind']=='VIDEO': check_video(p,m['profile'],scenes[j['scene_id']]['duration_seconds'])
                else: raise ValueError('unsupported type')
                sha=digest(p); actual=j['expected_filename']; note='Technical check only; manual visual QC required'
            except Exception as exc: status='REJECTED'; note=str(exc)
        results.append(dict(job_id=j['id'],attempt=j['attempt'],result=status,path=actual,sha256=sha,tool=None,notes=note,review_status='FAIL' if status=='REJECTED' else 'PENDING'))
    return {**b,'results':results}


def assemble(m, clips, audio, out):
    rows=timeline(m); profile=m['profile']; total=m['timing']['target_seconds']
    if any(r['overlap'] for r in rows): raise ValueError('overlap assembly not implemented; plan only')
    paths=[safe(clips,r['id']+'.mp4') for r in rows]
    for path,r in zip(paths,rows): check_video(path,profile,r['duration'])
    voices=voice_plan(m,audio); args=['ffmpeg','-v','error','-y']
    for path in paths: args+=['-i',str(path)]
    for v in voices: args+=['-i',v['path']]
    filters=[''.join(f'[{i}:v]' for i in range(len(paths)))+f'concat=n={len(paths)}:v=1:a=0[v]']
    if voices:
        for i,v in enumerate(voices): filters.append(f"[{len(paths)+i}:a]aresample=48000,adelay={round(v['start']*1000)}:all=1,apad[a{i}]")
        filters.append(''.join(f'[a{i}]' for i in range(len(voices)))+f'amix=inputs={len(voices)}:normalize=0,atrim=duration={total}[a]')
    args+=['-filter_complex',';'.join(filters),'-map','[v]']
    if voices: args+=['-map','[a]','-c:a','aac']
    args+=['-c:v','libx264','-pix_fmt','yuv420p','-threads','2','-t',str(total),str(out)]
    subprocess.run(args,check=True); return check_video(out,profile,total)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('command',choices=['build','batch-export','batch-import','voice-plan','render-still','card','assemble','probe']); p.add_argument('manifest'); p.add_argument('output'); p.add_argument('--root',default='.'); p.add_argument('--batch'); p.add_argument('--scene'); p.add_argument('--image'); p.add_argument('--groups'); p.add_argument('--font'); p.add_argument('--audio'); a=p.parse_args(); m=load(a.manifest)
    if a.command=='build': build(m,a.output)
    elif a.command=='batch-export': batch_export(m,a.root,a.output)
    elif a.command=='batch-import': save(a.output,batch_import(load(a.batch),m,a.root))
    elif a.command=='voice-plan': save(a.output,voice_plan(m,a.root))
    elif a.command=='render-still':
        s=next(s for s in m['scenes'] if s['id']==a.scene); print(render_still(a.image,a.output,m['profile'],s['duration_seconds'],s['motion_plan']))
    elif a.command=='card':
        groups=load(a.groups); card(a.output,m['profile'],groups['title'],groups['groups'],a.font)
    elif a.command=='assemble': print(assemble(m,a.root,a.audio,a.output))
    else: print(check_video(a.output,m['profile'],m['timing']['target_seconds']))


if __name__=='__main__': main()
