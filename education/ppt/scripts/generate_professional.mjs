import fs from 'node:fs';
import {buildPptx} from './build_professional.mjs';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('Usage: node generate_professional.mjs manifest.json output.pptx');
const m=JSON.parse(fs.readFileSync(input,'utf8'));
if(m.slides.length!==16||m.slides.some((s,i)=>s.id!=='P'+String(i+1).padStart(2,'0')||!s.speaker_notes||!Array.isArray(s.cards)||!s.cards.length))throw Error('Invalid professional draft manifest');
fs.writeFileSync(output,Buffer.from(buildPptx(m)));
