// Offline contract checks; subset of JSON Schema used by this repository, not a general implementation.
export function validateSchema(s,v,path="$"){
 let e=[];const fail=m=>e.push(path+": "+m);const type=x=>x==="null"?v===null:x==="array"?Array.isArray(v):x==="object"?v!==null&&typeof v==="object"&&!Array.isArray(v):x==="integer"?Number.isInteger(v):x==="number"?typeof v==="number"&&Number.isFinite(v):typeof v===x;
 if(s.type&&!(Array.isArray(s.type)?s.type:[s.type]).some(type)){fail("type");return e}
 if("const" in s&&v!==s.const)fail("const");
 if(s.enum&&!s.enum.includes(v))fail("enum");
 if(typeof v==="string"){if(s.minLength!==undefined&&v.length<s.minLength)fail("minLength");if(s.pattern&&!new RegExp(s.pattern).test(v))fail("pattern")}
 if(typeof v==="number"){if(s.minimum!==undefined&&v<s.minimum)fail("minimum");if(s.exclusiveMinimum!==undefined&&v<=s.exclusiveMinimum)fail("exclusiveMinimum")}
 if(Array.isArray(v)){if(s.minItems!==undefined&&v.length<s.minItems)fail("minItems");if(s.maxItems!==undefined&&v.length>s.maxItems)fail("maxItems");if(s.uniqueItems&&new Set(v.map(x=>JSON.stringify(x))).size!==v.length)fail("uniqueItems");if(s.items)v.forEach((x,i)=>e.push(...validateSchema(s.items,x,path+"["+i+"]")))}
 if(v!==null&&typeof v==="object"&&!Array.isArray(v)){for(const k of s.required||[])if(!Object.prototype.hasOwnProperty.call(v,k))fail("required "+k);for(const [k,x] of Object.entries(v)){if(s.properties?.[k])e.push(...validateSchema(s.properties[k],x,path+"."+k));else if(s.additionalProperties===false)fail("unexpected "+k)}}
 return e
}
export function validateRelations(m,f,l){
 const errors=[];const fail=x=>errors.push(x);const unique=(a,k)=>new Set(a.map(x=>x[k])).size===a.length;
 const same=(a,b)=>[...new Set(a)].sort().join("|")===[...new Set(b)].sort().join("|");
 const set=xs=>new Set(xs);const facts=set(f.facts.map(x=>x.id)),learn=set(l?.entries.map(x=>x.id)||[]),core=set(l?.core_attribute_codes||[]);
 if(m.event_id!==f.event_id||l&&m.event_id!==l.event_id)fail("event ID mismatch");
 if(m.source.sha256!==f.source.sha256||m.source.report_number!==f.source.report_number||m.source.report_date!==f.source.report_date)fail("source mismatch");
 if(m.artifact_type!=="INCIDENT_UNDERSTANDING"&&(!l||m.provenance.analysis_version!==l.analysis_version||m.provenance.standard_version!==l.standard_version))fail("analysis dependency");
 if(m.artifact_type==="INCIDENT_UNDERSTANDING"&&(m.provenance.analysis_version!==null||m.provenance.learning_ledger!==null))fail("incident must not depend on AI interpretation");
 if(!unique(f.facts,"id")||l&&!unique(l.entries,"id"))fail("duplicate ledger ID");
 if(l){if(l.core_attribute_codes.some(x=>l.additional_attribute_codes.includes(x)))fail("core/additional overlap");if(!same(l.entries.flatMap(x=>x.attribute_codes),l.core_attribute_codes))fail("learning coverage");for(const x of l.entries){if(x.fact_ids.some(y=>!facts.has(y)))fail("learning fact reference");if(!same(x.principle_codes,x.attribute_codes.map(y=>y.slice(0,2))))fail("learning principle grouping")}}
 const items=m.scenes||m.slides||[...m.questions,...m.scenarios,...m.actions];if(!unique(items,"id"))fail("duplicate item ID");
 const refs=m.references||[];if(!unique(refs,"id"))fail("duplicate reference ID");const refIDs=set(refs.map(x=>x.id));
 for(const x of items){if((x.fact_ids||[]).some(y=>!facts.has(y)))fail("unknown fact "+x.id);if((x.learning_ids||[]).some(y=>!learn.has(y)))fail("unknown learning "+x.id);if((x.attribute_codes||[]).some(y=>!core.has(y)))fail("noncore attribute "+x.id);if(x.attribute_codes?.length&&!same(x.principle_codes,x.attribute_codes.map(y=>y.slice(0,2))))fail("principle mismatch "+x.id);if((x.reference_ids||x.asset_ids||[]).some(y=>!refIDs.has(y)))fail("unknown asset "+x.id);if(x.scene_type==="FACT"&&!x.fact_ids.length)fail("fact scene missing facts");if(["INTERPRETATION","HYPOTHETICAL","ATTRIBUTE_SUMMARY"].includes(x.scene_type)&&!x.learning_ids.length)fail("learning scene missing learning");if(m.artifact_type==="INCIDENT_UNDERSTANDING"&&((x.learning_ids||[]).length||["INTERPRETATION","HYPOTHETICAL","ATTRIBUTE_SUMMARY"].includes(x.scene_type)))fail("incident mixed with interpretation");}
 if(m.scenes){const {width,height,aspect_ratio}=m.profile;const [w,h]=aspect_ratio.split(":").map(Number);if(Math.abs(width/height-w/h)>0.005)fail("aspect ratio mismatch");
 let total=0;for(let i=0;i<m.scenes.length;i++){const x=m.scenes[i],next=m.scenes[i+1];total+=x.duration_seconds-x.overlap_to_next_seconds;if(!next&&x.overlap_to_next_seconds!==0||next&&x.overlap_to_next_seconds>=Math.min(x.duration_seconds,next.duration_seconds))fail("invalid overlap "+x.id);
 if(x.render_mode==="I2V"&&!x.input_mode||x.render_mode!=="I2V"&&x.input_mode!==null)fail("I2V input mode "+x.id);if(x.render_mode==="STILL_MOTION"&&!x.motion_plan)fail("still motion missing "+x.id);
 if(x.transition==="OPENING"&&i!==0||i===0&&x.transition!=="OPENING")fail("opening transition");
 if(x.transition==="CONTINUOUS"&&(!x.location_id||x.location_id!==m.scenes[i-1]?.location_id))fail("invalid continuity");
 if(!unique(x.attempts,"take"))fail("duplicate take");if(x.accepted_take!==null&&!x.attempts.some(y=>y.take===x.accepted_take&&y.revision===m.revision&&y.result==="ACCEPTED"&&y.path&&y.sha256&&y.actual_seconds))fail("accepted take mismatch");
 if(x.scene_type==="ATTRIBUTE_SUMMARY"&&x.render_mode!=="CONTROLLED_GRAPHIC")fail("summary not controlled");
 }if(Math.abs(total-m.timing.target_seconds)>0.001)fail("timing mismatch");
 }
 if(m.artifact_type==="SAFETY_CULTURE_LEARNING"||m.artifact_type==="CLASSROOM_PPT"){const cards=items.filter(x=>(x.scene_type||x.layout)==="ATTRIBUTE_SUMMARY");if(cards.length!==1||!same(cards[0].attribute_codes,[...core]))fail("exactly one complete core-attribute summary required");}
 const a=m.approvals;if(["CONTENT_REVIEWED","ASSET_READY","EDITED","FINAL_QC","APPROVED"].includes(m.status)&&a.content_review!=="PASS")fail("content gate");if(["ASSET_READY","EDITED","FINAL_QC","APPROVED"].includes(m.status)&&a.asset_review!=="PASS")fail("asset gate");if(["FINAL_QC","APPROVED"].includes(m.status)&&a.final_qc!=="PASS")fail("final QC gate");if(m.status==="APPROVED"&&(!a.expert_approved||!a.reviewer||!a.review_record))fail("expert gate");if(a.expert_approved&&m.status!=="APPROVED")fail("approval status mismatch");
 return errors
}
export function validateBatch(b,m){const e=[];if(b.event_id!==m.event_id||b.artifact_id!==m.artifact_id||b.manifest_revision!==m.revision||b.aspect_ratio!==m.profile.aspect_ratio)e.push("batch dependency mismatch");const jobs=new Map();for(const j of b.jobs){if(jobs.has(j.id))e.push("duplicate job");jobs.set(j.id,j);const sc=m.scenes.find(x=>x.id===j.scene_id);if(!sc||sc.generation_route!=="GEMINI_TASKS_BATCH")e.push("invalid batch scene");if(j.reference_ids.some(x=>!m.references.some(r=>r.id===x)))e.push("unknown reference");}const resultKeys=new Set();for(const r of b.results){const k=r.job_id+":"+r.attempt;if(resultKeys.has(k))e.push("duplicate result");resultKeys.add(k);if(!jobs.has(r.job_id)||jobs.get(r.job_id).attempt!==r.attempt)e.push("unknown batch job/attempt");if(r.result==="ACCEPTED"&&(!r.path||!r.sha256||r.review_status!=="PASS"))e.push("unreviewed result");}return e}
