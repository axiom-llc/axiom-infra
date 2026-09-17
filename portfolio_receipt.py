#!/usr/bin/env python3
"""Run canonical local AXIOM portfolio checks and emit a revision-bound receipt."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, shutil, subprocess, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
ACTIVE=(
 'axiom-apex','axiom-api','axiom-ason','axiom-blender','axiom-demos','axiom-director',
 'axiom-harness','axiom-infra','axiom-llc.github.io','axiom-ops','axiom-rag','axiom-research','wiki-infinite',
)
CHECKS={
 'axiom-rag':[['python','-m','pytest','tests','-q']],
 'axiom-apex':[['python','-m','pytest','tests','-m','not integration and not host_isolation','-q']],
 'axiom-ason':[['python','-m','pytest','ason/tests','-q']],
 'axiom-api':[['python','-m','pytest','tests','-q']],
 'axiom-blender':[['make','test']],
 'axiom-demos':[['python','-m','pytest','tests','-q'],['python','-m','unittest','-v','test_config.py','test_executor.py','test_transcriber.py'],['make','test']],
 'axiom-director':[['python','-m','unittest','discover','-s','tests','-v'],['python','-m','director_state','check']],
 'axiom-harness':[['make','verify']],
 'axiom-infra':[['python','-m','unittest','discover','-s','tests','-v']],
 'axiom-llc.github.io':[['python','-m','unittest','discover','-s','tests','-v']],
 'axiom-ops':[['make','test']],
 'axiom-research':[['python','architecture/tests/check.py']],
 'wiki-infinite':[['python','-m','unittest','-v','tests/test_browser.py']],
}
def checks_for(name):
    if name=='axiom-api' and importlib.util.find_spec('responses') is None:
        return [['python','-m','compileall','-q','api_framework','gemini_client','tests'],['python','-c','from api_framework import APIClient; from gemini_client import GeminiClient']], 'partial', "dev-only dependency 'responses' unavailable; pytest not re-run"
    if name=='axiom-blender' and shutil.which('blender') is None:
        return [['python','-m','py_compile','scene.py'],['python','-c','import json; json.load(open("scene.example.json"))']], 'partial', 'Blender executable unavailable; headless render regression not run'
    if name=='wiki-infinite' and not (shutil.which('chromium') or shutil.which('chromium-browser')):
        return CHECKS[name], 'partial', 'Chromium unavailable; browser regression is expected to skip'
    return CHECKS[name], 'full', None
def run(cmd,cwd):
    actual=cwd
    if cwd.name=='axiom-demos' and cmd[:3]==['python','-m','unittest']: actual=cwd/'voice-commander'
    if cwd.name=='axiom-demos' and cmd[:2]==['make','test']: actual=cwd/'news-briefing'
    env=os.environ.copy(); siblings=[]
    if cwd.name=='axiom-apex': siblings=[ROOT/'axiom-rag']
    elif cwd.name=='axiom-ason': siblings=[ROOT/'axiom-apex',ROOT/'axiom-rag']
    if siblings:
        prefix=os.pathsep.join(str(x) for x in siblings); env['PYTHONPATH']=prefix+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['PYTHONDONTWRITEBYTECODE']='1'
    cp=subprocess.run(cmd,cwd=actual,text=True,capture_output=True,env=env)
    return {'command':cmd,'exit_code':cp.returncode,'stdout_tail':cp.stdout[-1200:],'stderr_tail':cp.stderr[-1200:]}
def git(repo):
    head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    status=subprocess.check_output(['git','-C',str(repo),'status','--porcelain=v1'],text=True).splitlines()
    return head,status
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def build(selected=None,allow_missing=False):
    names=list(selected) if selected else list(ACTIVE)
    repos={}; any_fail=False; any_limit=bool(selected); partial_coverage=bool(selected)
    for name in names:
        repo=ROOT/name
        if not (repo/'.git').is_dir():
            status='UNAVAILABLE' if allow_missing else 'MISSING'; repos[name]={'status':status,'coverage':'none','limitation':'repository checkout unavailable'}
            partial_coverage=True; any_limit |= allow_missing; any_fail |= not allow_missing; continue
        head,dirty=git(repo); checks,coverage,limitation=checks_for(name); results=[run(c,repo) for c in checks]
        passed=not dirty and all(r['exit_code']==0 for r in results); any_fail |= not passed; partial_coverage |= coverage!='full'; any_limit |= passed and coverage!='full'
        repos[name]={'head':head,'clean':not dirty,'working_tree':dirty[:20],'coverage':coverage,'limitation':limitation,'checks':results,'status':'PASS' if passed else 'FAIL'}
    overall='FAIL' if any_fail else ('PASS_WITH_LIMITS' if any_limit else 'PASS')
    coverage='partial' if partial_coverage else 'full'
    limitation=None if coverage=='full' else 'one or more repositories or checks are outside full validation coverage'
    body={'schema':'axiom-portfolio-validation/receipt-v2','generated_at':int(time.time()),'coverage':coverage,'limitation':limitation,'repositories':repos,'status':overall}
    body['receipt_sha256']=hashlib.sha256(canonical(body)).hexdigest(); return body
def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--repo',action='append',choices=sorted(ACTIVE)); ap.add_argument('--allow-missing',action='store_true'); ap.add_argument('-o','--output',type=Path)
    a=ap.parse_args(argv); receipt=build(a.repo,a.allow_missing); raw=json.dumps(receipt,indent=2)+'\n'
    if a.output: a.output.write_text(raw)
    print(raw,end=''); return 0 if receipt['status'] in {'PASS','PASS_WITH_LIMITS'} else 1
if __name__=='__main__': raise SystemExit(main())
