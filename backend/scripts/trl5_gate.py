#!/usr/bin/env python3
"""TRL-5 gate: checks measured evidence against docs/TRL5_READINESS.md criteria.

Stdlib only. Exit 0 only if every machine-checkable criterion passes.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "models" / "registry.json"
EXTERNAL_GLOB = "models/validation/external_*.json"


def _load(path):
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return None


def main() -> int:
    results = []
    reg = _load(REGISTRY) or {}
    results.append(("C1 active real-data model", bool(reg.get("current_model"))))

    ext = [d for d in (_load(p) for p in sorted(ROOT.glob(EXTERNAL_GLOB))) if d]
    real = [d for d in ext if d.get("data_source", "synthetic") != "synthetic"]
    results.append(("C2 external cohort present (real data)", bool(real)))

    def all_ok(fn):
        return bool(real) and all(fn(d) for d in real)

    results += [
        ("C2 n>=200, AUC>=0.80, CI low>=0.75",
         all_ok(lambda d: d.get("n", 0) >= 200 and d.get("auc", 0) >= 0.80
                and d.get("auc_ci_low", 0) >= 0.75)),
        ("C3 sensitivity & specificity >=0.80",
         all_ok(lambda d: d.get("sensitivity", 0) >= 0.80 and d.get("specificity", 0) >= 0.80)),
        ("C5 ECE<=0.10", all_ok(lambda d: d.get("ece", 1) <= 0.10)),
        ("C6 subgroup AUC gap<=0.05", all_ok(lambda d: d.get("subgroup_auc_gap", 1) <= 0.05)),
    ]
    ok = True
    for name, passed in results:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
        ok &= passed
    print("\nTRL 5 evidence:", "COMPLETE" if ok else "NOT YET (see docs/TRL5_READINESS.md)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
