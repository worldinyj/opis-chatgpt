function draw(s,n,shape){
 const N='1E293B', B='2563EB', T='0D9488', A='F59E0B', R='DC2626', P='6366F1', M='64748B', W='FFFFFF', G='F8FAFC', L='F1F5F9', S='334155';let o='';
 const rect=(x,y,w,h,c,geo='rect')=>{o+=shape(x,y,w,h,c,[],12,N,false,geo)};
 const tx=(x,y,w,h,t,z=19,c=N,b=false)=>{o+=shape(x,y,w,h,null,Array.isArray(t)?t:[t],z,c,b)};
 const card=(x,y,w,h,k,v,c=B,z=19)=>{rect(x,y,w,h,W,'roundRect');rect(x,y,.055,h,c);tx(x+.22,y+.19,w-.42,.42,k,15,c,true);tx(x+.22,y+(h>3?1.20:.78),w-.42,h-(h>3?1.34:.92),v,z,N,true)};
 const strip=(t,c=B)=>{rect(.55,5.91,12.23,.60,L,'roundRect');tx(.76,6.04,11.8,.35,t,16,c,true)};
 const footer=()=>{rect(.55,6.82,12.23,.018,'E2E8F0');tx(.56,6.96,11.4,.30,'KINS 2025-07호 · 분석 v0.1.1 | 교육용 초안 · 전문가 승인 전',10,M);tx(12.1,6.94,.64,.32,('0'+n).slice(-2),12,M,true)};
 rect(0,0,13.333333,7.5,G);
 if(s.kind==='cover'){
  rect(0,0,13.333333,7.5,N);rect(8.9,0,4.43,7.5,S);rect(9.2,.6,3.5,5.25,'26384E','roundRect');rect(9.55,.95,2.8,4.55,'2E435F','roundRect');rect(9.89,1.30,2.12,3.85,'354F70','roundRect');rect(.65,1.57,.08,3.03,'3B82F6');tx(.85,.65,8,.45,'SAFETY CULTURE CASE STUDY',16,'93C5FD',true);tx(.88,1.62,8.0,2.2,s.title,35,W,true);tx(.9,4.00,7.9,.65,s.lead,22,'93C5FD',true);tx(.9,5.12,7.65,.60,s.cards[0][1],18,W);rect(0,6.70,13.333333,.8,'0F172A');tx(.7,6.92,11.95,.38,'250919W2  |  KINS 2025-07호  |  교육용 초안 · 전문가 승인 전',14,'CBD5E1');return o;
 }
 const dark=['flow','metrics','end'].includes(s.kind);if(dark)rect(0,0,13.333333,1.40,N);rect(.52,.40,.075,.60,s.accent||B);tx(.74,.35,10.75,.65,s.title,26,dark?W:N,true);tx(.75,1.00,11.5,.35,s.section,12,dark?'CBD5E1':M);tx(11.45,.46,1.42,.33,s.label,10,dark?'93C5FD':s.accent||B,true);
 const c=s.accent||B, a=s.cards;
 if(s.kind==='timeline'){
  rect(1.05,2.25,11.15,.045,'CBD5E1');a.forEach(([k,v],i)=>{const x=.55+i*4.15,cc=[B,A,T][i];rect(x+1.75,1.98,.55,.55,cc,'ellipse');card(x,2.70,3.94,2.66,k,v,cc,20)});
 }else if(n===3){
  a.forEach(([k,v],i)=>card(.55+i*3.08,1.72,2.99,2.12,k,v,[B,P,T,A][i],18));rect(.55,4.05,12.23,1.55,S,'roundRect');tx(.82,4.25,2.25,.36,'사건 요약',16,'93C5FD',true);tx(3.0,4.25,9.4,1.04,'초기 이상과 작업 중단 이후 누설이 확인되어 대응이 이루어졌다.',22,W,true);
 }else if(s.kind==='metrics'){
  rect(.55,1.70,4.0,3.98,S,'roundRect');tx(.83,2.00,3.5,.50,a[0][0],17,'93C5FD',true);tx(.83,2.73,3.48,1.02,a[0][1],32,W,true);tx(.83,4.25,3.45,1.10,['회수 1,306.01','외부 배출 5.14 kg-D2O'],17,'CBD5E1');a.slice(1).forEach(([k,v],i)=>card(4.76+(i%2)*4.08,1.70+Math.floor(i/2)*2.06,3.94,1.91,k,v,[T,B,P,A][i],18));
 }else if(s.kind==='attributes'){
  a.forEach(([k,v],i)=>card(.55+(i%2)*6.18,1.67+Math.floor(i/2)*1.35,6.0,1.23,k,v,[B,B,P,P,T,T][i],15));
 }else if(s.kind==='principles'){
  rect(.55,1.66,12.23,.51,N);tx(.78,1.77,2.2,.30,'안전문화 원칙',15,W,true);tx(3.42,1.77,8.8,.30,'현장 행동 및 학습 근거',15,W,true);a.forEach(([k,v],i)=>{const y=2.25+i*1.12;rect(.55,y,12.23,1.01,i%2===0?W:L);rect(.55,y,.05,1.01,c);tx(.77,y+.18,2.5,.73,k,18,c,true);tx(3.43,y+.18,9.0,.72,v,19,N)});
 }else if(s.kind==='flow'||s.kind==='discussion'||s.kind==='end'){
  rect(.55,1.70,4.0,3.98,S,'roundRect');tx(.82,2.05,3.45,.60,s.kind==='discussion'?'현장 질문':s.kind==='end'?'핵심 교훈':'학습 목표',19,'93C5FD',true);tx(.82,2.94,3.45,s.kind==='discussion'?1.25:2.40,s.lead,25,W,true);if(s.kind==='discussion')tx(.82,4.55,3.45,.90,['개인: 질의·근거 기록','팀: 후속조치·효과 확인'],16,'CBD5E1');a.forEach(([k,v],i)=>{const y=1.70+i*1.36;rect(4.76,y,8.02,1.22,W,'roundRect');rect(4.76,y,.055,1.22,[B,T,P][i]);tx(4.99,y+.14,2.1,.78,k,17,[B,T,P][i],true);tx(7.20,y+.17,5.27,.78,v,19,N,true)});
 }else{
  const cols=a.length===3?3:2,w=cols===3?3.94:6.0,h=a.length===4?1.88:3.75;
  a.forEach(([k,v],i)=>card(.55+(i%cols)*(cols===3?4.15:6.18),1.75+Math.floor(i/cols)*2.02,w,h,k,v,[c,T,P,A][i],a.length===4?19:23));
 }
 strip(s.lead,c);footer();return o;
}
// Dependency-free deterministic native OOXML PPTX generator; no API calls.
function buildPptx(m){
 const A='http://schemas.openxmlformats.org/drawingml/2006/main', P='http://schemas.openxmlformats.org/presentationml/2006/main', R='http://schemas.openxmlformats.org/officeDocument/2006/relationships', PK='http://schemas.openxmlformats.org/package/2006/relationships', CT='http://schemas.openxmlformats.org/package/2006/content-types';
 const XML='<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', ns=`xmlns:a="${A}" xmlns:r="${R}" xmlns:p="${P}"`, files={};
 const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); const em=n=>Math.round(n*914400);
 const rel=rows=>XML+`<Relationships xmlns="${PK}">`+rows.map(([id,type,target])=>`<Relationship Id="${id}" Type="${R}/${type}" Target="${target}"/>`).join('')+'</Relationships>';
 const group='<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>';
 const color=c=>`<a:solidFill><a:srgbClr val="${c}"/></a:solidFill>`; const xfrm=(x,y,w,h)=>`<a:xfrm><a:off x="${em(x)}" y="${em(y)}"/><a:ext cx="${em(w)}" cy="${em(h)}"/></a:xfrm>`;
 const run=(t,size,c,b=false)=>`<a:r><a:rPr lang="ko-KR" sz="${size*100}" b="${b?1:0}">${color(c)}<a:latin typeface="Noto Sans CJK KR"/><a:ea typeface="Noto Sans CJK KR"/></a:rPr><a:t>${esc(t)}</a:t></a:r>`;
 const para=(t,size,c,b=false)=>`<a:p><a:pPr algn="l"/><a:r>${''}</a:r>${run(t,size,c,b)}<a:endParaRPr lang="ko-KR"/></a:p>`.replace('<a:r></a:r>','');
 let id=1;
 const shape=(x,y,w,h,fill,lines=[],size=22,c='19344B',bold=false,geo='rect')=>{const k=++id;return `<p:sp><p:nvSpPr><p:cNvPr id="${k}" name="Editable ${k}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr><p:spPr>${xfrm(x,y,w,h)}<a:prstGeom prst="${geo}"><a:avLst/></a:prstGeom>${fill?color(fill):'<a:noFill/>'}<a:ln><a:noFill/></a:ln></p:spPr><p:txBody><a:bodyPr wrap="square" lIns="0" rIns="0" tIns="0" bIns="0" anchor="t"/><a:lstStyle/>${(lines.length?lines:['']).map(t=>para(t,size,c,bold)).join('')}</p:txBody></p:sp>`};
 const bg='F3F6F8', navy='16364D', teal='287C80', muted='526778', white='FFFFFF';
 const master=XML+`<p:sldMaster ${ns}><p:cSld name="OPIS"><p:spTree>${group}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>`;
 const map='<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>';
 files['ppt/slideMasters/slideMaster1.xml']=master;
 files['ppt/slideMasters/_rels/slideMaster1.xml.rels']=rel([['rId1','slideLayout','../slideLayouts/slideLayout1.xml'],['rId2','theme','../theme/theme1.xml']]);
 files['ppt/slideLayouts/slideLayout1.xml']=XML+`<p:sldLayout ${ns} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>${group}</p:spTree></p:cSld>${map}</p:sldLayout>`;
 files['ppt/slideLayouts/_rels/slideLayout1.xml.rels']=rel([['rId1','slideMaster','../slideMasters/slideMaster1.xml']]);
 const clr=[['dk1','16364D'],['lt1','FFFFFF'],['dk2','526778'],['lt2','F3F6F8'],['accent1','287C80'],['accent2','456C89'],['accent3','BB9C66'],['accent4','559C86'],['accent5','64748B'],['accent6','96A8BA'],['hlink','287C80'],['folHlink','456C89']];
 const fnt='<a:latin typeface="Noto Sans CJK KR"/><a:ea typeface="Noto Sans CJK KR"/><a:cs typeface="Arial"/>';
 files['ppt/theme/theme1.xml']=XML+`<a:theme xmlns:a="${A}" name="OPIS"><a:themeElements><a:clrScheme name="OPIS">${clr.map(([k,c])=>`<a:${k}><a:srgbClr val="${c}"/></a:${k}>`).join('')}</a:clrScheme><a:fontScheme name="OPIS"><a:majorFont>${fnt}</a:majorFont><a:minorFont>${fnt}</a:minorFont></a:fontScheme><a:fmtScheme name="OPIS"><a:fillStyleLst>${color(navy)+color(teal)+color(white)}</a:fillStyleLst><a:lnStyleLst>${[9525,25400,38100].map(w=>`<a:ln w="${w}">${color(navy)}</a:ln>`).join('')}</a:lnStyleLst><a:effectStyleLst>${'<a:effectStyle><a:effectLst/></a:effectStyle>'.repeat(3)}</a:effectStyleLst><a:bgFillStyleLst>${color(white)+color(bg)+color(navy)}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>`;
 files['ppt/notesMasters/notesMaster1.xml']=XML+`<p:notesMaster ${ns}><p:cSld><p:spTree>${group}</p:spTree></p:cSld><p:clrMap accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" bg1="lt1" bg2="lt2" folHlink="folHlink" hlink="hlink" tx1="dk1" tx2="dk2"/><p:notesStyle/></p:notesMaster>`;
 files['ppt/notesMasters/_rels/notesMaster1.xml.rels']=rel([['rId1','theme','../theme/theme1.xml']]);
 for(let i=0;i<m.slides.length;i++){
  const s=m.slides[i], n=i+1;id=1;let sh=draw(s,n,shape);
  files[`ppt/slides/slide${n}.xml`]=XML+`<p:sld ${ns}><p:cSld><p:spTree>${group}${sh}</p:spTree></p:cSld>${map}</p:sld>`;
  files[`ppt/slides/_rels/slide${n}.xml.rels`]=rel([['rId1','slideLayout','../slideLayouts/slideLayout1.xml'],['rId2','notesSlide',`../notesSlides/notesSlide${n}.xml`]]);
  const notes=esc(s.speaker_notes);files[`ppt/notesSlides/notesSlide${n}.xml`]=XML+`<p:notes ${ns}><p:cSld><p:spTree>${group}<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Placeholder"/><p:cNvSpPr/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr>${xfrm(.5,1,6.5,8)}</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="ko-KR"/><a:t>${notes}</a:t></a:r><a:endParaRPr lang="ko-KR"/></a:p></p:txBody></p:sp></p:spTree></p:cSld>${map}</p:notes>`;
  files[`ppt/notesSlides/_rels/notesSlide${n}.xml.rels`]=rel([['rId1','notesMaster','../notesMasters/notesMaster1.xml'],['rId2','slide',`../slides/slide${n}.xml`]]);
 }
 files['_rels/.rels']=rel([['rId1','officeDocument','ppt/presentation.xml']]);
 files['ppt/presentation.xml']=XML+`<p:presentation ${ns}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rId2"/></p:notesMasterIdLst><p:sldIdLst>${m.slides.map((s,i)=>`<p:sldId id="${256+i}" r:id="rId${i+3}"/>`).join('')}</p:sldIdLst><p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>`;
 files['ppt/_rels/presentation.xml.rels']=rel([['rId1','slideMaster','slideMasters/slideMaster1.xml'],['rId2','notesMaster','notesMasters/notesMaster1.xml'],...m.slides.map((s,i)=>[`rId${i+3}`,'slide',`slides/slide${i+1}.xml`])]);
 const ct={'ppt/presentation.xml':'presentation.main','ppt/slideMasters/slideMaster1.xml':'slideMaster','ppt/slideLayouts/slideLayout1.xml':'slideLayout','ppt/notesMasters/notesMaster1.xml':'notesMaster'};for(let n=1;n<=m.slides.length;n++){ct[`ppt/slides/slide${n}.xml`]='slide';ct[`ppt/notesSlides/notesSlide${n}.xml`]='notesSlide'}
 files['[Content_Types].xml']=XML+`<Types xmlns="${CT}"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>${Object.entries(ct).map(([p,t])=>`<Override PartName="/${p}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.${t}+xml"/>`).join('')}<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/></Types>`;
 // STORE ZIP, deterministic timestamp and member order. All paths ASCII.
 const utf=s=>{const out=[];for(const c of s){const x=c.codePointAt(0);if(x<128)out.push(x);else if(x<2048)out.push(192|(x>>6),128|(x&63));else if(x<65536)out.push(224|(x>>12),128|((x>>6)&63),128|(x&63));else out.push(240|(x>>18),128|((x>>12)&63),128|((x>>6)&63),128|(x&63))}return out};
 const crc=b=>{let c=0xffffffff;for(const x of b){c^=x;for(let j=0;j<8;j++)c=(c>>>1)^((c&1)?0xedb88320:0)}return (c^0xffffffff)>>>0};const u16=(a,v)=>a.push(v&255,(v>>>8)&255),u32=(a,v)=>a.push(v&255,(v>>>8)&255,(v>>>16)&255,(v>>>24)&255),append=(a,b)=>{for(const x of b)a.push(x)};
 const out=[],central=[];for(const [name,val] of Object.entries(files)){const n=utf(name),b=utf(val),c=crc(b),off=out.length;u32(out,0x04034b50);[20,0,0,0,33].forEach(v=>u16(out,v));[c,b.length,b.length].forEach(v=>u32(out,v));u16(out,n.length);u16(out,0);append(out,n);append(out,b);u32(central,0x02014b50);[20,20,0,0,0,33].forEach(v=>u16(central,v));[c,b.length,b.length].forEach(v=>u32(central,v));[n.length,0,0,0,0].forEach(v=>u16(central,v));u32(central,0);u32(central,off);append(central,n)}const off=out.length;append(out,central);u32(out,0x06054b50);[0,0,Object.keys(files).length,Object.keys(files).length].forEach(v=>u16(out,v));u32(out,central.length);u32(out,off);u16(out,0);return out;
}
export {buildPptx};
