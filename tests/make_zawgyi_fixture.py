#!/usr/bin/env python3
"""Generate a Zawgyi fixture for the validator tests.

This is a test helper, not part of the skill. It ports the U2Z transliteration
rules from the reference `myanmar-tools` package (Apache-2.0, Google Inc.) so
the fixture contains authentic Zawgyi rather than hand-typed approximations.

    python3 tests/make_zawgyi_fixture.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RULES_SRC = Path("/tmp/mmnpm/package/resources/U2Z.js")

OBJ_RE = re.compile(
    r"\{\s*p:\s*RegExp\((.*?)\),\s*s:\s*'(.*?)',\s*\}", re.DOTALL
)
STR_RE = re.compile(r"'((?:[^'\\]|\\.)*)'")


JS_ESCAPES = {
    "n": "\n", "t": "\t", "r": "\r", "'": "'", '"': '"',
    "\\": "\\", "/": "/", "`": "`",
}


def js_unescape(text: str) -> str:
    """Decode a JavaScript string literal, keeping unknown escapes literal.

    `\\1` in a replacement means a capture backreference, so it must survive
    as the two characters backslash and digit rather than becoming chr(1).
    """
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "u" and i + 5 < len(text) + 1:
                out.append(chr(int(text[i + 2:i + 6], 16)))
                i += 6
                continue
            if nxt in JS_ESCAPES:
                out.append(JS_ESCAPES[nxt])
                i += 2
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def parse_rules(src: str) -> list[list[tuple[str, str]]]:
    phases: list[list[tuple[str, str]]] = []
    for block in re.findall(r"var rules\d+ = \[(.*?)\n  \];", src, re.DOTALL):
        rules: list[tuple[str, str]] = []
        for m in OBJ_RE.finditer(block):
            parts = STR_RE.findall(m.group(1))
            pattern = "".join(js_unescape(p) for p in parts)
            # JavaScript uses $1 for capture groups; Python's re.expand uses \1.
            replacement = re.sub(r"\$(\d)", r"\\\1", js_unescape(m.group(2)))
            rules.append((pattern, replacement))
        phases.append(rules)
    return phases


def run_phase(rules: list[tuple[str, str]], text: str) -> str:
    """Port of myanmar-tools `runPhase` for `^`-anchored rules."""
    out = ""
    mid = text
    while mid:
        found = False
        for pattern, replacement in rules:
            m = re.match(pattern, mid)
            if m:
                found = True
                right = len(mid) - len(m.group(0))
                mid = mid[: m.start()] + m.expand(replacement) + mid[m.end():]
                new_start = len(mid) - right
                out += mid[:new_start]
                mid = mid[new_start:]
        if not found:
            out += mid[0]
            mid = mid[1:]
    return out


def convert(text: str, phases) -> str:
    for rules in phases:
        text = run_phase(rules, text)
    return text


if __name__ == "__main__":
    if not RULES_SRC.exists():
        print(
            f"error: {RULES_SRC} not found. The fixture is already committed; "
            "this script is only needed to regenerate it.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    phases = parse_rules(RULES_SRC.read_text(encoding="utf-8"))
    source = (
        "မင်္ဂလာပါသော။ ယနေ့ ကိုဒ်အသစ်တွေ ရေးတယ်။ "
        "နည်းလမ်းက လွယ်လွယ်ပါတယ်။ "
        "စမ်းကြည့်ပြီး ပြန်လည်မှတ်တမ်းတင်ပါ။"
    )
    print(convert(source, phases))
