// Expert review preparation: read-only, proposals only.
export function preparePacket(row, r, metadata, standard, link, hashes) {
  const def = new Map(standard.principles.flatMap(p=>p.attributes.map(a=>[a.code,a.definition])));
  const errors=[], notes=[];
  const same=(a,b)=>a&&b&&[...a].sort().join("|")===[...b].sort().join("|");
  if(r.event_id!==row.event_id||r.queue_id!==row.queue_id||hashes.normalized!==row.blob||r.entries.length!==40||r.validation.status!=="PASS_STRUCTURAL"||r.can_ship!==false) errors.push("NORMALIZED_RECORD");
  const analysis=metadata.split(/^analysis:\s*$/m)[1]||"";
  function array(key) {
    const m=analysis.match(new RegExp("^\\s{2}"+key+":\\s*\\[([^\\]]*)\\]\\s*$","m"));
    if(!m)return null;
    const x=m[1].split(",").map(t=>t.trim().replace(/^["']|["']$/g,"")).filter(Boolean);
    return x.every(c=>def.has(c))&&new Set(x).size===x.length?x:null;
  }
  const expected={candidate_attributes:r.legacy.index_candidates,additional_review_attributes:r.legacy.additional_review,insufficient_or_low_relevance_attributes:r.entries.filter(x=>x.role==="INSUFFICIENT_OR_LOW_RELEVANCE_LEGACY").map(x=>x.code),approved_attributes:r.legacy.approved_attributes};
  const checks=Object.entries(expected).map(([key,expected])=>{
    const actual=array(key);
    return {key,status:actual===null?"UNPARSED":same(actual,expected)?"MATCH":"DIFFERENCE",metadata_only:actual?.filter(x=>!expected.includes(x))??null,normalized_only:actual===null?null:expected.filter(x=>!actual.includes(x))};
  });
  const candidate=r.entries.filter(x=>["DIRECT_REVIEW_CANDIDATE","INDIRECT_REVIEW_CANDIDATE"].includes(x.role));
  const learning=r.entries.filter(x=>["EDUCATION_ONLY","POSITIVE_LEARNING"].includes(x.role));
  const toItem=x=>({code:x.code,name:x.name,definition:def.get(x.code),role:x.role,fact_ids:x.evidence.fact_refs,source_refs:x.evidence.source_refs,author_rationale:x.evidence.rationale,learning_ids:x.learning_ids,link_review:link?.code===x.code?{disposition:link.author_disposition,question:link.expert_question,proposal_path:row.path.replace("ATTRIBUTE_ROLES_V1.json","PHASE3D_LINK_REVIEW_20261126.json")}:null,expert_question:link?.code===x.code?link.expert_question:"표준 정의와 원본의 지적이 실제로 부합하는가? 반증·범위·추가 근거를 확인할 것.",decision:"PENDING",reviewer_reason:null});
  const items=candidate.map(toItem), education=learning.map(toItem);
  if(items.length+education.length!==r.legacy.learning_core.length||new Set([...items,...education].map(x=>x.code)).size!==r.legacy.learning_core.length)errors.push("CORE_COVERAGE");
  if(link&&(!items.some(x=>x.code===link.code)||link.provenance.normalized_blob!==hashes.normalized))errors.push("LINK_PROVENANCE");
  const noDirect=!candidate.some(x=>x.role==="DIRECT_REVIEW_CANDIDATE");
  const priority=link?"P1_LINK_REVIEW":noDirect?"P1_EVIDENCE_BOUNDARY":r.entries.some(x=>x.role==="EDUCATION_ONLY")?"P2_ROLE_BOUNDARY":"P3_STANDARD_REVIEW";
  return {schema_version:"1.0",event_id:r.event_id,queue_id:r.queue_id,priority,source_commit:hashes.source_commit,provenance:{normalized_path:row.path,normalized_blob:hashes.normalized,metadata_blob:hashes.metadata,standard_blob:hashes.standard,link_index_blob:hashes.link,source_sha256:r.provenance.source_sha256},source_paths:{report:row.path.replace("review_package/ATTRIBUTE_ROLES_V1.json","report.md"),fact_ledger:row.path.replace("review_package/ATTRIBUTE_ROLES_V1.json","media/fact_ledger.json"),learning_ledger:row.path.replace("review_package/ATTRIBUTE_ROLES_V1.json","media/learning_ledger.json")},candidates:items,education_and_positive:education,additional_review_codes:r.entries.filter(x=>x.role==="ADDITIONAL_REVIEW_PENDING").map(x=>x.code),legacy_unselected_codes:r.entries.filter(x=>x.role==="INSUFFICIENT_OR_LOW_RELEVANCE_LEGACY").map(x=>x.code),metadata_checks:checks,validation:{status:errors.length?"FAIL":"PASS_STRUCTURAL",errors,notes},expert_status:"PENDING",expert_reviewer:null,expert_review_date:null,approved_attributes:[],confirmed_weakness_count:null,can_ship:false};
}
