"""Score model answers against a sample file.

Usage:
    python validators/check.py samples/ee6_editing_sample.json answers.jsonl

answers.jsonl has one JSON object per line: {"id": "<test id>", "output": "<model answer>"}
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from basic import validate  # noqa: E402
from validator_ee6 import evaluate_edit  # noqa: E402


def main(suite_path: str, answers_path: str) -> int:
    with open(suite_path, encoding="utf-8") as f:
        tests = {t["id"]: t for t in json.load(f)["tests"]}
    answers = {}
    with open(answers_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                a = json.loads(line)
                answers[a["id"]] = a.get("output", "")

    passed = 0
    for tid, test in tests.items():
        out = answers.get(tid)
        if out is None:
            print(f"{tid:24} MISSING")
            continue
        if test.get("validator") == "toimetamine":
            res = evaluate_edit(test, out)
            failed = [k for k, v in res["kontrollid"].items() if not v]
            ok = res["passed"]
            note = "" if ok else "failed: " + ", ".join(failed)
        else:
            res = validate(test, out)
            ok = res["passed"]
            note = "" if ok else ("right value, wrong format" if res["decision_passed"] else "wrong")
        passed += ok
        print(f"{tid:24} {'PASS' if ok else 'FAIL'}  {note}")
    print(f"\n{passed}/{len(tests)} passed")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2]))
