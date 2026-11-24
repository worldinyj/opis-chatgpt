import fs from 'node:fs';
import {buildPptx} from './build_pptx.mjs';
const [input,output]=process.argv.slice(2);
if(!input||!output)throw Error('Usage: node generate.mjs slide_manifest.json output.pptx');
const m=JSON.parse(fs.readFileSync(input,'utf8'));
if(m.artifact_type!=='CLASSROOM_PPT'||m.profile.aspect_ratio!=='16:9'||!m.profile.editable_native_elements||m.slides.some(s=>!s.speaker_notes||!s.body.length||s.body.length>(s.layout==='ATTRIBUTE_SUMMARY'?6:3)))throw Error('Unsupported manifest/layout; review before building');
fs.writeFileSync(output,Buffer.from(buildPptx(m)));
