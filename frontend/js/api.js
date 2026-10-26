import {state} from './state.js';
export async function api(path, body, method=body===undefined?'GET':'POST') {
  const response=await fetch(`/api${path}`,{method,headers:{'Content-Type':'application/json','X-HalawaCore-Token':state.token},body:body===undefined?undefined:JSON.stringify(body),cache:'no-store'});
  let result;
  try{result=await response.json();}catch{throw new Error('Backend returned an unreadable response.');}
  if(!response.ok) throw new Error(result.error?.message || `Request failed (${response.status})`);
  return result;
}
