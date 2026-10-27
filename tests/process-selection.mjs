import assert from 'node:assert/strict';
import {processKey,reconcileSelection,commonCpus} from '../frontend/js/process-selection.js';

const a={pid:10,identity:'100',name:'same-name'},b={pid:20,identity:'200',name:'same-name'};
const selected=new Map([[processKey(a),a],[processKey(b),b]]);
// Filter/sort do not affect membership; refresh updates rows by PID and start identity.
assert.deepEqual([...reconcileSelection(selected,[b,a]).keys()],[processKey(a),processKey(b)]);
assert.equal(reconcileSelection(selected,[a,{...b,identity:'201'}]).size,1);
assert.equal(reconcileSelection(selected,[]).size,0);
assert.deepEqual(commonCpus([[0,2,8,8],[2,8],[2,8,10]],[0,2,10]),[2]);
assert.deepEqual(commonCpus([[0],[2]],[0,2]),[]);
assert.deepEqual(commonCpus([[0,2],null],[0,2]),[]);
assert.deepEqual(commonCpus([[0,2],[]],[0,2]),[]);
assert.deepEqual(commonCpus([],[0,2]),[]);
console.log('Process selection identity and shared-CPU constraints passed.');
