import fs from 'node:fs';
import {runTests} from './tests.mjs';
const p=process.argv[2];if(!p)throw Error('Specify standards/safety_culture_40.json');runTests(JSON.parse(fs.readFileSync(p,'utf8')));
