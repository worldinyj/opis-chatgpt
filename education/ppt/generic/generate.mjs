import fs from 'node:fs';
import {prepare,buildPptx} from './generic.mjs';
const [input,standard,output]=process.argv.slice(2);
if(!input||!standard||!output)throw Error('Usage: node generate.mjs input.json standards.json output.pptx');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const m=prepare(read(input),read(standard));
fs.writeFileSync(output,Buffer.from(buildPptx(m)));
fs.writeFileSync(output+'.prepared.json',JSON.stringify(m,null,2)+'\n');
