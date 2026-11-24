import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateSchema,validateRelations,validateBatch} from '../scripts/validate_contract.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const base='cases/2025/250919W2/media/';
const f=read(base+'fact_ledger.json'),l=read(base+'learning_ledger.json');
const schema=n=>read('video/schemas/'+n+'.schema.json');
const list=[['production','incident_understanding/production.json'],['production','safety_culture_learning/production.json'],['production','shorts/SHORT-01/production.json'],['ppt','classroom_ppt/slide_manifest.json'],['discussion_action','discussion_action/manifest.json']];
let errors=[...validateSchema(schema('fact_ledger'),f),...validateSchema(schema('learning_ledger'),l)];
for(const [s,p] of list){const m=read(base+p);errors.push(...validateSchema(schema(s),m),...validateRelations(m,f,m.artifact_type==='INCIDENT_UNDERSTANDING'?null:l));}
const b=read(base+'safety_culture_learning/batch_job.example.json'),m=read(base+'safety_culture_learning/production.json');errors.push(...validateSchema(schema('batch_job'),b),...validateBatch(b,m));
if(errors.length){console.error(errors);process.exit(1)}console.log('Pilot 8 documents and cross-reference contract: PASS');
