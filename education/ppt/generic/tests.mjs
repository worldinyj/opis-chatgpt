import assert from 'node:assert/strict';
import {prepare,buildPptx} from './generic.mjs';
import {syntheticFixture} from './fixtures.mjs';
export function runTests(standard){
 let n=0;const test=(name,fn)=>{fn();console.log('PASS',name);n++};const base=()=>syntheticFixture();const reject=(change)=>{const m=base();change(m);assert.throws(()=>prepare(m,standard))};
 for(let k=12;k<=16;k++)test('slide count '+k,()=>assert.equal(prepare(syntheticFixture(k),standard).slides.length,k));
 test('deterministic binary',()=>{const m=prepare(base(),standard);assert.deepEqual(buildPptx(m),buildPptx(m))});
 test('unknown code',()=>reject(m=>m.core_attribute_codes.push('ZZ1')));
 test('duplicate core',()=>reject(m=>m.core_attribute_codes.push(m.core_attribute_codes[0])));
 test('overlap',()=>reject(m=>m.additional_attribute_codes.push(m.core_attribute_codes[0])));
 test('missing learning',()=>reject(m=>m.learning[0].attribute_codes=[]));
 test('missing fact ref',()=>reject(m=>m.slides[3].fact_ids=['MISSING']));
 test('missing summary links',()=>reject(m=>m.slides.find(s=>s.pattern==='ATTR').learning_ids=[]));
 test('approval blocked',()=>reject(m=>m.can_ship=true));
 test('missing pattern',()=>reject(m=>m.slides[3].pattern='CAUSE'));
 test('wrong size',()=>reject(m=>m.target_slides=15));
 test('manual summary blocked',()=>reject(m=>m.slides.find(s=>s.pattern==='ATTR').cards=[['fake','fake']]));
 test('zero candidates explicit',()=>{const m=base();m.core_attribute_codes=[];m.additional_attribute_codes=[];assert.equal(prepare(m,standard).slides.find(s=>s.pattern==='ATTR').title,'0개 관련 원칙 · 0개 핵심 후보')});
 test('ten principles',()=>{const m=base();m.core_attribute_codes=standard.principles.map(p=>p.attributes[0].code);m.additional_attribute_codes=[];m.learning[0].attribute_codes=m.core_attribute_codes;const s=prepare(m,standard).slides.find(s=>s.pattern==='ATTR');assert.equal(s.cards.length,10);assert.equal(s.cards.flatMap(x=>x[1]).length,10)});
 test('forty dense codes rejected rather than omitted',()=>{const m=base();m.core_attribute_codes=standard.principles.flatMap(p=>p.attributes.map(a=>a.code));m.additional_attribute_codes=[];m.learning[0].attribute_codes=m.core_attribute_codes;assert.throws(()=>prepare(m,standard),/too dense/)});
 test('metric detail from new case',()=>{const s=prepare(base(),standard).slides.find(s=>s.pattern==='METRIC');assert.equal(s.detail,'시험용 보조 수치 8.1')});
 console.log('PASS TOTAL',n);return n;
}
