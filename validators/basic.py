"""Deterministic validators used by EE4 (one_of) and EE5 (json_exact).

Strict by design: the answer must match the contract exactly. A model that
gives the right value inside a code block it was told not to use fails
`passed`, but `decision_passed` shows the value itself was right.
"""
import json
import re
from typing import Any, Dict


def _clean(output: str) -> str:
    return re.sub(r"<think>.*?</think>", "", output or "", flags=re.DOTALL).strip()


def _from_code_block(raw: str) -> Any:
    for part in raw.split("```")[1:]:
        block = part.strip()
        if block.startswith("json"):
            block = block[4:].strip()
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    return None


def validate(test: Dict[str, Any], output: str) -> Dict[str, Any]:
    raw = _clean(output)
    kind = test.get("validator", "exact")
    expected = test["expected"]
    contract = decision = False

    if kind == "one_of":
        last = raw.splitlines()[-1].strip() if raw else ""
        contract = raw in expected
        decision = contract or last in expected
    elif kind == "exact":
        last = raw.splitlines()[-1].strip() if raw else ""
        contract = raw == expected
        decision = contract or last == expected
    elif kind == "json_exact":
        try:
            contract = decision = json.loads(raw) == expected
        except json.JSONDecodeError:
            decision = _from_code_block(raw) == expected
    else:
        raise ValueError(f"unknown validator: {kind}")

    return {"passed": contract, "contract_passed": contract, "decision_passed": decision}
