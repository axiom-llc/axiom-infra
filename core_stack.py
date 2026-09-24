#!/usr/bin/env python3
"""Exercise the canonical local ASON→APEX→RAG stack without provider generation."""
from __future__ import annotations
import hashlib,json,os,subprocess,urllib.request
from pathlib import Path
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent
def post(url,body,headers):
    req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json',**headers},method='POST')
    with urllib.request.urlopen(req,timeout=15) as r: return json.load(r)
def get(url,headers):
    req=urllib.request.Request(url,headers=headers);
    with urllib.request.urlopen(req,timeout=15) as r: return json.load(r)
def revisions():
    out={}
    for n in ('axiom-rag','axiom-apex','axiom-ason','axiom-infra','axiom-demos'):
        p=ROOT/n
        if (p/'.git').is_dir(): out[n]=subprocess.check_output(['git','-C',str(p),'rev-parse','HEAD'],text=True).strip()
    return out
def run():
    rag_token=os.environ['RAG_API_TOKEN']; apex_key=os.environ['APEX_API_KEY']
    inspect=post('http://127.0.0.1:8000/v1/inspect',{'namespace':'documents-gemini-embedding-2'},{'Authorization':'Bearer '+rag_token})
    plan={'plan':{'steps':[{'tool':'write_file','args':{'path':'/tmp/axiom-core-stack.txt','content':'core-stack-reference'}},{'tool':'read_file','args':{'path':'/tmp/axiom-core-stack.txt'}}]}}
    cp=subprocess.run(['docker','compose','run','--rm','-T','ason','submit','-','--authority-ref','core-stack:offline-reference'],cwd=HERE,input=json.dumps(plan),text=True,capture_output=True)
    if cp.returncode: raise RuntimeError(cp.stderr or cp.stdout)
    submitted=json.loads(cp.stdout); response=submitted['apex_response']; auth=submitted['authorization']; detail=get(f"http://127.0.0.1:8080/runs/{response['run_id']}",{'X-Apex-Key':apex_key})
    if detail.get('authorization')!=auth or detail.get('ledger',{}).get('plan_digest')!=auth.get('approved_plan_digest'): raise RuntimeError('durable authorization binding mismatch')
    result={'schema':'axiom-core-stack/reference-v1','status':'PASS','repositories':revisions(),'rag':{'namespace':inspect.get('namespace'),'exists':inspect.get('exists')},'apex':{'run_id':response['run_id'],'status':response['status'],'plan_digest':auth['approved_plan_digest']},'authorization':{'authorization_id':auth['authorization_id'],'authority_ref':auth['authority_ref'],'policy_digest_or_ref':auth['policy_digest_or_ref']}}
    result['evidence_sha256']=hashlib.sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest(); return result
def main(): print(json.dumps(run(),indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
