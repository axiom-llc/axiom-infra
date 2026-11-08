"""Infra native generator, workload equivalence and real Git reverse."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from rsi.native import GenerationError, generate, propose, validate_rule
from rsi.benchmark import isolate, load, measure

ROOT=Path(__file__).resolve().parents[1]
RULE=json.loads((ROOT/"rsi/generators.json").read_text())["rules"][0]
SRC=(ROOT/RULE["path"]).read_text()


class NativeInfraTests(unittest.TestCase):
    def test_revision_bound_and_stable_generator(self):
        r=generate(ROOT)
        self.assertEqual(len(r["candidates"]),1)
        self.assertFalse(r["mutation_authority"])
        self.assertEqual(propose(SRC,RULE,"a"*40),propose(SRC,RULE,"a"*40))
        self.assertIsNone(propose(SRC.replace(RULE["before"],RULE["after"],1),RULE,"a"*40))
        with self.assertRaises(GenerationError):
            generate(ROOT,"a"*40)

    def test_unsafe_and_ambiguous_sources(self):
        for p in ("../x.py","/secret.py","rsi/native.py","tests/test_x.py"):
            with self.assertRaises(GenerationError):
                validate_rule({**RULE,"path":p})
        with self.assertRaises(GenerationError):
            propose(SRC+RULE["before"],RULE,"a"*40)

    def test_exact_reverse_and_isolated_semantics(self):
        patch=propose(SRC,RULE,"a"*40)["patch"]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            f=root/RULE["path"]
            f.write_text(SRC)
            prior=f.read_bytes()
            subprocess.run(["git","init","-q"],cwd=root,check=True)
            for args in (("apply","--check","-"),("apply","-"),
                         ("apply","-R","--check","-"),("apply","-R","-")):
                subprocess.run(["git",*args],cwd=root,input=patch,text=True,check=True,
                               capture_output=True)
            self.assertEqual(f.read_bytes(),prior)
            a,b=load(SRC),load(SRC.replace(RULE["before"],RULE["after"],1))
            for name in a["ACTIVE"]:
                (root/name/".git").mkdir(parents=True)
            x,y=isolate(a,root),isolate(b,root)
            self.assertEqual(x(),y())
            self.assertEqual(x(["axiom-infra"]),y(["axiom-infra"]))

    def test_independent_paired_benchmark(self):
        result=measure(ROOT)
        self.assertEqual(result["paired_samples"],11)
        self.assertTrue(result["quality_equivalent"])
        self.assertFalse(result["promotion_authorized"])


if __name__=="__main__":
    unittest.main()
