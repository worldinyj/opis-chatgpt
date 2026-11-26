// Phase 3-C. Pure transformation of pinned legacy records; no source mutation.
export function normalizeCase(row, standard, fact, learning, review, hashes) {
  const roles = {D:"DIRECT_REVIEW_CANDIDATE",I:"INDIRECT_REVIEW_CANDIDATE",H:"EDUCATION_ONLY",P:"POSITIVE_LEARNING"};
  const taxonomy = standard.principles.flatMap(p=>p.attributes.map(a=>({code:a.code,name:a.name,principle:p.code})));
  const codes = taxonomy.map(a=>a.code), issues=[], warnings=[];
  const fail = (cond, msg) => {if (!cond) issues.push(msg)};
  const unique = x=>Array.isArray(x)&&new Set(x).size===x.length;
  const same=(x,y)=>Array.isArray(x)&&Array.isArray(y)&&[...x].sort().join("|")===[...y].sort().join("|");
  const {event_id,queue_id}=row;
  fail(codes.length===40&&unique(codes),"TAXONOMY_COUNT");
  fail([fact,learning,review].every(x=>x.event_id===event_id)&&review.queue_id===queue_id,"EVENT_ID");
  fail(review.standard_blob===hashes.standard&&review.fact_ledger_blob===hashes.fact&&review.learning_ledger_blob===hashes.learning,"REVIEW_INPUT_HASH");
  const core=learning.core_attribute_codes, extra=learning.additional_attribute_codes, legacy=row.legacy_index_candidates;
  fail(unique(core)&&unique(extra)&&unique(legacy)&&[...core,...extra,...legacy].every(c=>codes.includes(c)),"LEGACY_CODES");
  fail(!core.some(c=>extra.includes(c)),"CORE_ADDITIONAL_OVERLAP");
  fail(unique(review.codes.map(x=>x.code))&&same(review.codes.map(x=>x.code),core),"REVIEW_CORE_COVERAGE");
  fail(unique(fact.facts.map(x=>x.id))&&unique(learning.entries.map(x=>x.id)),"LEDGER_IDS");
  const fMap=new Map(fact.facts.map(x=>[x.id,x]));
  fail(same([...new Set(learning.entries.flatMap(x=>x.attribute_codes))],core),"LEARNING_CORE_COVERAGE");
  for(const x of learning.entries) fail(x.fact_ids.every(id=>fMap.has(id)),"LEARNING_FACT_REF:"+x.id);
  for(const [k,field] of Object.entries({D:"direct_review_candidates",I:"indirect_review_candidates",H:"education_only",P:"positive_learning"}))
    fail(same(row[field],review.codes.filter(x=>x.evidence_class===k).map(x=>x.code)),"SUMMARY_ROLE:"+k);
  fail(Array.isArray(row.approved_attributes)&&row.approved_attributes.length===0,"APPROVAL_REQUIRES_SEPARATE_MIGRATION");
  fail(review.can_ship===false&&row.can_ship===false,"RELEASE_GATE");
  const recordMap=new Map(review.codes.map(x=>[x.code,x]));
  const entries=taxonomy.map(t=>{
    const r=recordMap.get(t.code), ls=learning.entries.filter(x=>x.attribute_codes.includes(t.code));
    let role=r?roles[r.evidence_class]:extra.includes(t.code)?"ADDITIONAL_REVIEW_PENDING":"INSUFFICIENT_OR_LOW_RELEVANCE_LEGACY";
    if(r) {
      fail(!!role&&r.proposed_review_only===true&&typeof r.rationale==="string"&&!!r.rationale.trim(),"EVIDENCE_RECORD:"+t.code);
      fail(unique(r.fact_refs)&&r.fact_refs.length>0&&r.fact_refs.every(id=>fMap.has(id)),"REVIEW_FACT_REF:"+t.code);
      const linked=new Set(ls.flatMap(x=>x.fact_ids));
      if(!r.fact_refs.some(id=>linked.has(id)))warnings.push({code:t.code,type:"NO_SHARED_LEARNING_FACT",note:"Review evidence and existing learning evidence do not intersect; assess meaning, do not auto-edit."});
    }
    return {...t,role,legacy_index_candidate:legacy.includes(t.code),legacy_learning_core:core.includes(t.code),legacy_additional:extra.includes(t.code),
      review_scope:r?"CORE_AUTHOR_REVIEW":"LEGACY_ONLY_NOT_INDIVIDUALLY_REVIEWED",
      evidence:r?{classification:r.evidence_class,fact_refs:r.fact_refs,rationale:r.rationale,source_refs:r.fact_refs.filter(id=>fMap.has(id)).map(id=>{const f=fMap.get(id);return {fact_id:id,kind:f.kind,section:f.section,pdf_pages:f.pdf_pages,printed_pages:f.printed_pages}})}:null,
      learning_ids:ls.map(x=>x.id),expert_status:"PENDING",expert_decision:null};
  });
  const counts=entries.reduce((o,x)=>(o[x.role]=(o[x.role]||0)+1,o),{});
  const excluded=entries.filter(x=>x.legacy_index_candidate&&["EDUCATION_ONLY","POSITIVE_LEARNING"].includes(x.role)).map(x=>x.code);
  const missing=entries.filter(x=>x.legacy_learning_core&&!x.legacy_index_candidate).map(x=>x.code);
  if(excluded.length)warnings.push({type:"LEGACY_INDEX_NON_WEAKNESS_ROLE",codes:excluded});
  if(missing.length)warnings.push({type:"LEARNING_CORE_NOT_IN_LEGACY_INDEX",codes:missing});
  fail(entries.length===40&&unique(entries.map(x=>x.code)),"PARTITION");
  return {schema_version:"1.0",event_id,queue_id,standard_version:learning.standard_version,analysis_version:learning.analysis_version,source_commit:hashes.source_commit,
    provenance:{standard_blob:hashes.standard,fact_ledger_blob:hashes.fact,learning_ledger_blob:hashes.learning,review_blob:hashes.review,review_path:row.review_file,phase3b_summary_blob:hashes.summary,source_sha256:fact.source.sha256},
    entries,counts,legacy:{index_candidates:legacy,learning_core:core,additional_review:extra,approved_attributes:row.approved_attributes},
    changes:{excluded_from_proposed_weakness_view:excluded,learning_not_in_legacy_index:missing,source_data_mutated:false},
    validation:{status:issues.length?"FAIL":"PASS_STRUCTURAL",errors:issues,warnings,semantic_validation:"PENDING",original_pdf_reinspection:"PENDING"},
    approved_attributes:[],confirmed_weakness_count:null,can_ship:false};
}
