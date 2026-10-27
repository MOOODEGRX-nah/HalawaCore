export const processKey=process=>`${process.pid}:${process.identity}`;
export const selectionLimit=32;

// Reconcile against the complete process list, never against a search result.
export function reconcileSelection(selection,rows){
  const current=new Map(rows.map(row=>[processKey(row),row]));
  return new Map([...selection.keys()].filter(key=>current.has(key)).map(key=>[key,current.get(key)]));
}

// A shared experiment may only narrow every existing task's current mask.
export function commonCpus(masks,online){
  if(!masks.length||masks.some(mask=>!Array.isArray(mask)||!mask.length))return [];
  return [...new Set(masks[0])].filter(cpu=>online.includes(cpu)&&masks.every(mask=>mask.includes(cpu))).sort((a,b)=>a-b);
}
