#!/usr/bin/env python3
"""Validate the canonical unreleased AXIOM core compatibility set."""
from __future__ import annotations
import argparse, json, tomllib
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
MANIFEST=HERE/'release-compatibility.json'

def load(): return json.loads(MANIFEST.read_text())
def validate():
    m=load(); errors=[]
    if m.get('publication_authorized') is not False: errors.append('manifest must not authorize publication')
    for name in m.get('order',[]):
        spec=m['packages'][name]; py=ROOT/name/'pyproject.toml'
        if not py.is_file(): errors.append(f'{name}: checkout missing'); continue
        project=tomllib.loads(py.read_text()).get('project',{})
        if project.get('version') != spec['version']: errors.append(f"{name}: expected {spec['version']}, found {project.get('version')}")
        deps=set(project.get('dependencies',[]))
        for required in spec.get('requires',[]):
            if required not in deps: errors.append(f'{name}: missing exact compatibility dependency {required}')
    return m,errors

def main(argv=None):
    ap=argparse.ArgumentParser(); ap.add_argument('--json',action='store_true'); a=ap.parse_args(argv)
    m,errors=validate(); out={'release_set':m.get('release_set'),'order':m.get('order'),'status':'PASS' if not errors else 'FAIL','errors':errors,'publication_authorized':False}
    print(json.dumps(out,indent=2) if a.json else (out['status']+('\n'+'\n'.join(errors) if errors else '')))
    return 0 if not errors else 1
if __name__=='__main__': raise SystemExit(main())
