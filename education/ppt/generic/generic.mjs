// Draft-only reusable 16:9 layouts. Case data are supplied, never inferred.
const PATTERNS=['COVER','FACT','TIME','CAUSE','PRINC','ATTR','METRIC','ACTION','END'];
const names={PA:'개인 책임',QA:'의문 제기',CO:'안전중심 의사소통',LA:'리더십',DM:'의사결정',WE:'상호 존중 업무환경',CL:'지속적 학습',PI:'문제 파악 및 해결',RC:'안전 우려 제기',WP:'작업 프로세스'};
const fail=t=>{throw Error(t)};
const nonempty=x=>typeof x==='string'&&x.trim().length>0;
const uniq=a=>Array.isArray(a)&&new Set(a).size===a.length;
const units=t=>[...t].reduce((n,c)=>n+(c.codePointAt(0)>255?2:1),0);
function attributeColumns(groups){
 for(const size of [16,15,14,13]){
  const cols=[[],[]], heights=[0,0], step=size/72*1.37, maxUnits=Math.floor(5.48*72/size*1.66);
  for(const [heading,items] of groups){let lines=[],line='';for(const item of items){if(units(item)>maxUnits)fail('Attribute label too long');const next=line?line+' · '+item:item;if(units(next)>maxUnits){lines.push(line);line=item}else line=next}if(line)lines.push(line);const h=.34+lines.length*step+.10, j=heights[0]<=heights[1]?0:1;cols[j].push({heading,lines,h});heights[j]+=h+.07}
  if(Math.max(...heights)<=4.12)return {cols,size,step};
 }fail('Attribute summary too dense: redesign one page, do not drop codes');
}
function prepare(input,standard){
 const m=JSON.parse(JSON.stringify(input));
 if(m.schema_version!=='1.0'||m.can_ship!==false||m.status!=='DESIGN_DRAFT'||!['REAL_DRAFT','SYNTHETIC_TEST'].includes(m.case_type))fail('Draft-only input');
 if(!nonempty(m.event_id)||!nonempty(m.analysis_version)||!m.source||!['issuer','report_number','report_date'].every(k=>nonempty(m.source[k])))fail('Missing provenance');
 if(m.case_type==='REAL_DRAFT'&&!/^[a-f0-9]{64}$/.test(m.source.sha256||''))fail('Source hash required');
 if(!Array.isArray(standard.principles)||standard.principles.length!==10)fail('Taxonomy must have 10 principles');
 const attrs=new Map();for(const p of standard.principles){if(!names[p.code])fail('Unknown principle');for(const a of p.attributes){if(attrs.has(a.code)||!a.code.startsWith(p.code)||!nonempty(a.name))fail('Invalid taxonomy');attrs.set(a.code,{p:p.code,name:a.name})}}
 if(attrs.size!==40)fail('Taxonomy must have 40 attributes');
 if(m.standard_version!=='1.0'||!uniq(m.fact_ids)||!Array.isArray(m.learning)||!uniq(m.learning.map(x=>x.id))||!uniq(m.core_attribute_codes)||!uniq(m.additional_attribute_codes))fail('Invalid ledger reference lists');
 const all=[...m.core_attribute_codes,...m.additional_attribute_codes];if(!uniq(all)||all.some(x=>!attrs.has(x)))fail('Unknown or overlapping attribute code');
 const ids=new Set(m.learning.map(x=>x.id));if(m.learning.some(x=>!nonempty(x.id)||!uniq(x.attribute_codes)||x.attribute_codes.some(c=>!attrs.has(c))))fail('Invalid learning entries');
 if(m.core_attribute_codes.some(c=>!m.learning.some(l=>l.attribute_codes.includes(c))))fail('Core code lacks learning entry');
 if(!Array.isArray(m.slides)||m.slides.length<12||m.slides.length>16||m.slides.length!==m.target_slides||!uniq(m.slides.map(s=>s.id)))fail('Explicit 12–16 slide plan required');
 if(m.slides[0].pattern!=='COVER'||m.slides.at(-1).pattern!=='END'||PATTERNS.some(p=>!m.slides.some(s=>s.pattern===p))||m.slides.filter(s=>s.pattern==='ATTR').length!==1)fail('Required layout patterns / single attribute page');
 for(const s of m.slides){
  if(!PATTERNS.includes(s.pattern)||!['id','title','section','label','lead','speaker_notes'].every(k=>nonempty(s[k]))||!Number.isInteger(s.minutes)||s.minutes<1||!uniq(s.fact_ids)||!uniq(s.learning_ids)||s.fact_ids.some(x=>!m.fact_ids.includes(x))||s.learning_ids.some(x=>!ids.has(x)))fail('Invalid slide / evidence: '+s.id);
  if(s.pattern==='ATTR'){
   if(s.cards?.length)fail('Attribute cards are generated, not supplied');
   if(m.core_attribute_codes.some(c=>!m.learning.some(l=>s.learning_ids.includes(l.id)&&l.attribute_codes.includes(c))))fail('Summary learning links incomplete');
   const groups=new Map();for(const c of m.core_attribute_codes){const a=attrs.get(c);if(!groups.has(a.p))groups.set(a.p,[]);groups.get(a.p).push(c+' '+a.name)}
   s.cards=[...groups].map(([p,items])=>[p+' '+names[p],items]);if(!s.cards.length)s.cards=[['선정된 핵심 후보 없음',['근거 부족 또는 미선정은 양호 판정이 아님']]];
   s.title=groups.size+'개 관련 원칙 · '+m.core_attribute_codes.length+'개 핵심 후보';s.lead='교육용 후보 · 공식 평가 아님 · 미선정은 양호 판정 아님';s.attribute_layout=attributeColumns(s.cards);
   s.speaker_notes+=' | 핵심 후보: '+(m.core_attribute_codes.join(', ')||'없음')+'; 추가 검토: '+(m.additional_attribute_codes.join(', ')||'없음')+'; 선정 개수는 심각도 점수가 아님.';
  }else{
   const max=s.pattern==='METRIC'||s.pattern==='TIME'?5:s.pattern==='COVER'?1:s.pattern==='PRINC'||s.pattern==='END'?3:4;
   if(!Array.isArray(s.cards)||s.cards.length<1||s.cards.length>max||(s.pattern==='TIME'&&s.cards.length<2)||s.cards.some(c=>!Array.isArray(c)||c.length!==2||!c.every(nonempty)))fail('Invalid cards: '+s.id);
   if(s.pattern==='FACT'&&!nonempty(s.detail))fail('Fact summary required: '+s.id);
   if(s.pattern==='METRIC'&&s.detail!==undefined&&!nonempty(s.detail))fail('Invalid metric detail');
  }
  if(s.accent&&!/^[A-Fa-f0-9]{6}$/.test(s.accent))fail('Invalid accent');
  s.speaker_notes+=' | 근거 ID: '+([...s.fact_ids,...s.learning_ids].join(', ')||'교육 구성');
 }
 m.footer=m.source.issuer+' '+m.source.report_number+' · 분석 v'+m.analysis_version+' | '+(m.case_type==='SYNTHETIC_TEST'?'가상 테스트 · 실제 사건 아님':'교육용 초안 · 전문가 승인 전');
 m.cover_footer=m.event_id+' | '+m.source.issuer+' '+m.source.report_number+' | '+(m.case_type==='SYNTHETIC_TEST'?'가상 테스트 · 실제 사건 아님':'교육용 초안 · 전문가 승인 전');
 return m;
}
function draw(s,n,shape,m){
 const N='1E293B', B='2563EB', T='0D9488', A='F59E0B', P='6366F1', M='64748B', W='FFFFFF', G='F8FAFC', L='F1F5F9', S='334155';let o='';const c=s.accent||B, a=s.cards;
 const rect=(x,y,w,h,f,geo='rect')=>{o+=shape(x,y,w,h,f,[],12,N,false,geo)};
 const tx=(x,y,w,h,t,z=19,f=N,b=false)=>{o+=shape(x,y,w,h,null,Array.isArray(t)?t:String(t).split('\n'),z,f,b)};
 const card=(x,y,w,h,k,v,f=c,z=19)=>{rect(x,y,w,h,W,'roundRect');rect(x,y,.055,h,f);tx(x+.19,y+.15,w-.38,.49,k,15,f,true);tx(x+.19,y+.72,w-.38,h-.84,v,z,N,true)};
 rect(0,0,13.333333,7.5,G);
 if(s.pattern==='COVER'){
  rect(0,0,13.333333,7.5,N);rect(9.0,0,4.333333,7.5,S);for(let i=0;i<3;i++)rect(9.25+i*.32,.65+i*.36,3.4-i*.64,5.2-i*.72,['26384E','2E435F','354F70'][i],'roundRect');rect(.64,1.53,.08,3.10,'3B82F6');tx(.88,.65,8,.45,s.label,16,'93C5FD',true);tx(.88,1.58,8.0,2.25,s.title,35,W,true);tx(.88,4.02,8.0,.70,s.lead,22,'93C5FD',true);tx(.88,5.05,8,.65,a[0][1],18,W);rect(0,6.70,13.333333,.8,'0F172A');tx(.70,6.92,12,.40,m.cover_footer,14,'CBD5E1');return o;
 }
 const dark=['METRIC','END'].includes(s.pattern);if(dark)rect(0,0,13.333333,1.40,N);rect(.52,.40,.075,.60,c);tx(.74,.35,10.65,.65,s.title,26,dark?W:N,true);tx(.75,1.00,11.4,.35,s.section,12,dark?'CBD5E1':M);tx(11.45,.46,1.42,.38,s.label,10,dark?'93C5FD':c,true);
 if(s.pattern==='TIME'){
  const w=(12.23-.16*(a.length-1))/a.length;rect(1.02,2.18,11.27,.045,'CBD5E1');a.forEach(([k,v],i)=>{const x=.55+i*(w+.16),f=[B,A,T,P,M][i];rect(x+w/2-.24,1.96,.48,.48,f,'ellipse');card(x,2.68,w,2.80,k,v,f,a.length>3?16:20)});
 }else if(s.pattern==='FACT'){
  const w=(12.23-.16*(a.length-1))/a.length;a.forEach(([k,v],i)=>card(.55+i*(w+.16),1.72,w,2.12,k,v,[B,P,T,A][i],18));rect(.55,4.05,12.23,1.55,S,'roundRect');tx(.82,4.25,2.25,.36,'사건 요약',16,'93C5FD',true);tx(3.0,4.25,9.4,1.04,s.detail,20,W,true);
 }else if(s.pattern==='METRIC'){
  rect(.55,1.70,4,3.98,S,'roundRect');tx(.83,2.00,3.5,.70,a[0][0],17,'93C5FD',true);tx(.83,2.83,3.48,1.35,a[0][1],28,W,true);if(s.detail)tx(.83,4.40,3.45,1.04,s.detail,16,'CBD5E1');const rest=a.slice(1),cols=rest.length===1?1:2,w=cols===1?8.02:3.94,h=rest.length>2?1.91:3.98;rest.forEach(([k,v],i)=>card(4.76+(i%cols)*4.08,1.70+Math.floor(i/cols)*2.06,w,h,k,v,[T,B,P,A][i],18));
 }else if(s.pattern==='ATTR'){
  const {cols,size,step}=s.attribute_layout;cols.forEach((col,j)=>{let y=1.64;for(const g of col){const x=.55+j*6.18;rect(x,y,6.00,g.h,W,'roundRect');rect(x,y,.05,g.h,c);tx(x+.16,y+.045,5.68,.31,g.heading,Math.max(13,size),c,true);g.lines.forEach((line,k)=>tx(x+.16,y+.35+k*step,5.68,step+.025,line,size,N));y+=g.h+.07}});
 }else if(s.pattern==='PRINC'){
  rect(.55,1.66,12.23,.51,N);tx(.78,1.77,2.65,.32,'원칙 / 주제',15,W,true);tx(3.55,1.77,8.8,.32,'현장 행동 및 학습 근거',15,W,true);a.forEach(([k,v],i)=>{const y=2.25+i*1.12;rect(.55,y,12.23,1.01,i%2===0?W:L);rect(.55,y,.05,1.01,c);tx(.77,y+.16,2.65,.77,k,18,c,true);tx(3.55,y+.16,8.9,.77,v,19,N)});
 }else if(s.pattern==='END'||(s.pattern==='ACTION'&&s.variant==='panel')){
  rect(.55,1.70,4,3.98,S,'roundRect');tx(.82,2.06,3.45,.55,s.pattern==='END'?'핵심 교훈':'학습 및 실천',19,'93C5FD',true);tx(.82,2.86,3.45,1.38,s.lead,23,W,true);if(s.detail)tx(.82,4.43,3.45,1.0,s.detail,16,'CBD5E1');const h=(3.98-.12*(a.length-1))/a.length;a.forEach(([k,v],i)=>{const y=1.70+i*(h+.12);rect(4.76,y,8.02,h,W,'roundRect');rect(4.76,y,.055,h,[B,T,P,A][i]);tx(4.99,y+.14,2.1,h-.27,k,17,[B,T,P,A][i],true);tx(7.20,y+.14,5.27,h-.27,v,18,N,true)});
 }else{
  const cols=a.length===3?3:a.length===1?1:2,w=(12.23-.16*(cols-1))/cols,h=a.length===4?1.91:3.75;a.forEach(([k,v],i)=>card(.55+(i%cols)*(w+.16),1.75+Math.floor(i/cols)*2.04,w,h,k,v,[c,T,P,A][i],a.length===4?18:21));
 }
 rect(.55,5.92,12.23,.60,L,'roundRect');tx(.76,6.04,11.8,.37,s.lead,16,c,true);rect(.55,6.82,12.23,.018,'E2E8F0');tx(.56,6.96,11.35,.30,m.footer,10,M);tx(12.1,6.94,.64,.32,String(n).padStart(2,'0'),12,M,true);return o;
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
  const s=m.slides[i], n=i+1;id=1;let sh=draw(s,n,shape,m);
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
export {buildPptx,prepare};
