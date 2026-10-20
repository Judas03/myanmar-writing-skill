#!/usr/bin/env python3
"""Regression tests for the mechanical Burmese-content validator.

These tests intentionally do not claim to measure native writing quality.
Behavioral quality is reviewed with tests/eval_cases.md and approved samples.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATE = ROOT / ".opencode/skills/myanmar-writing/scripts/validate.py"
FIXTURES = ROOT / "tests/fixtures"


def run(fixture: str, register: str = "professional", fmt: str = "generic"):
    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATE),
            str(FIXTURES / fixture),
            "--register",
            register,
            "--format",
            fmt,
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print(f"validator did not emit JSON for {fixture}:\n{proc.stdout}\n{proc.stderr}")
        return proc.returncode, {"findings": []}
    return proc.returncode, payload


def ids(payload: dict, severity: str | None = None) -> set[str]:
    return {
        finding["id"]
        for finding in payload.get("findings", [])
        if severity is None or finding["severity"] == severity
    }


def main() -> int:
    failures: list[str] = []

    print("mechanical findings")
    code, payload = run("defects.md", "casual", "generic")
    required_errors = {"PUN-003", "STY-003"}
    missing = required_errors - ids(payload, "error")
    if missing:
        failures.append(f"defects.md missing errors: {sorted(missing)}")
    else:
        print("  ok    defects.md catches punctuation and placeholders")
    if code != 1:
        failures.append(f"defects.md exit {code}, expected 1")

    code, payload = run("script-boundary.md", "casual", "facebook")
    if "MIX-002" not in ids(payload, "warn"):
        failures.append("script-boundary.md missing MIX-002 warning")
    else:
        print("  ok    script-boundary.md reports a readability warning")
    if code != 0:
        failures.append(f"script-boundary.md exit {code}, expected 0")

    code, payload = run("zawgyi-source.md", "casual", "generic")
    if "ENC-001" not in ids(payload):
        failures.append("zawgyi-source.md missing ENC-001")
    else:
        print("  ok    zawgyi-source.md is detected")

    code, payload = run("clean.md", "casual", "facebook")
    if payload.get("errors"):
        failures.append(f"clean.md has {payload['errors']} unexpected errors")
    else:
        print("  ok    clean.md has no errors")

    print("\ncli behaviour")
    cases = [
        (["--register", "nonsense", str(FIXTURES / "clean.md")], 2, "bad register"),
        (["--format", "nonsense", str(FIXTURES / "clean.md")], 2, "bad format"),
        ([str(FIXTURES / "does-not-exist.md")], 2, "missing file"),
    ]
    for args, expected, label in cases:
        proc = subprocess.run(
            [sys.executable, str(VALIDATE), *args], capture_output=True, text=True
        )
        if proc.returncode != expected:
            failures.append(f"{label}: exit {proc.returncode}, expected {expected}")
        else:
            print(f"  ok    {label} -> exit {expected}")

    proc = subprocess.run(
        [
            sys.executable,
            str(VALIDATE),
            str(FIXTURES / "script-boundary.md"),
            "--format",
            "facebook",
            "--strict",
            "--quiet",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 1:
        failures.append(f"strict warning exit {proc.returncode}, expected 1")
    else:
        print("  ok    --strict turns warnings into exit 1")

    proc = subprocess.run(
        [sys.executable, str(VALIDATE), "-", "--format", "web", "--json"],
        input="မြန်မာAPI ကို သုံးပါတယ်။\n",
        capture_output=True,
        text=True,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        failures.append("stdin --json did not emit valid JSON")
    else:
        if "MIX-002" not in ids(payload, "warn"):
            failures.append("stdin did not report MIX-002")
        else:
            print("  ok    stdin and JSON mode work")

    print()
    if failures:
        print(f"FAILED — {len(failures)} problem(s):")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
