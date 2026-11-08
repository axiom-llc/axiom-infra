"""Synthetic stubbed portfolio orchestration benchmark; no real Git or provider."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from statistics import median
import tempfile
import time
from types import SimpleNamespace
from rsi.native import generate


def load(source):
    ns={"__name__":"rsi_infra_receipt",
        "__file__":str(Path(__file__).resolve().parents[1] / "portfolio_receipt.py")}
    exec(compile(source,"portfolio_receipt.py","exec"),ns)
    return ns


def fake_check(cmd,repo):
    return {"command":cmd,"exit_code":0,"stdout_tail":"","stderr_tail":""}


def isolate(ns, root):
    ns["ROOT"]=root
    ns["time"]=SimpleNamespace(time=lambda: 1740000000)
    ns["git"]=lambda p: ("a"*40,[])
    ns["checks_for"]=lambda n: ([["true"]],"full",None)
    ns["run"]=fake_check
    return ns["build"]


def measure(root):
    receipt=generate(root)
    if len(receipt["candidates"])!=1:
        return {"status":"NO_APPLICABLE_RULE"}
    rule=json.loads((root/"rsi/generators.json").read_text())["rules"][0]
    source=(root/rule["path"]).read_text()
    updated=source.replace(rule["before"],rule["after"],1)
    original=load(source)
    candidate=load(updated)
    if original["ACTIVE"]!=candidate["ACTIVE"]:
        raise ValueError("portfolio scope changed")
    with tempfile.TemporaryDirectory() as d:
        checkout=Path(d)
        for name in original["ACTIVE"]:
            (checkout/name/".git").mkdir(parents=True)
        a=isolate(original,checkout)
        b=isolate(candidate,checkout)
        examples=[
            ((),{}), ((),{"selected":["axiom-infra"]}),
            ((),{"selected":["axiom-rag","axiom-ops"]}),
            ((),{"selected":[]}),
            ((),{"selected":("axiom-infra","axiom-rag")}),
            ((),{"selected":["missing"],"allow_missing":True}),
            ((),{"selected":["missing"],"allow_missing":False}),
        ]
        for positional,kwargs in examples:
            if a(*positional,**kwargs)!=b(*positional,**kwargs):
                raise ValueError("portfolio report/digest behavior changed")
        samples=[]
        for i in range(11):
            order=(("base",a),("candidate",b)) if i%2==0 else (
                ("candidate",b),("base",a))
            result={}
            for label,fn in order:
                start=time.perf_counter_ns()
                for _ in range(200):
                    fn(["axiom-infra"])
                result[label]=(time.perf_counter_ns()-start)/200
            samples.append(result)
    baseline=median(x["base"] for x in samples)
    updated_ns=median(x["candidate"] for x in samples)
    return {
        "schema":"axiom-native-rsi/benchmark-v1",
        "source_revision":receipt["source_revision"],
        "candidate_id":receipt["candidates"][0]["candidate_id"],
        "source_sha256":sha256(source.encode()).hexdigest(),
        "candidate_sha256":sha256(updated.encode()).hexdigest(),
        "workload_provenance":"synthetic single-selected-repo orchestration with stubbed Git/CI",
        "paired_samples":11,"operations_per_sample":200,
        "baseline_median_ns_per_op":baseline,"candidate_median_ns_per_op":updated_ns,
        "gain_percentage":100*(baseline-updated_ns)/baseline if baseline else None,
        "quality_equivalent":True,"promotion_authorized":False,
        "status":"POSITIVE_MACHINE_MEASUREMENT" if updated_ns<baseline else "NONPOSITIVE_MEASUREMENT",
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=measure(Path(__file__).resolve().parents[1])
    if args.output:
        args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps(report,sort_keys=True))
