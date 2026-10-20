#!/usr/bin/env python3
"""Check mechanical defects in Burmese (Myanmar) content.

Usage:
    python3 validate.py <file|-> [--register professional|casual|formal|diaspora]
                         [--format facebook|web|blog|generic]
                         [--json] [--strict] [--quiet]

Exit codes:
    0  clean (warnings may still be reported)
    1  errors found (or warnings, with --strict)
    2  could not run (bad arguments, unreadable file, missing dependency)

Design notes:
    * Standard library only. `myanmartools` is optional and enables accurate
      Zawgyi detection; without it the script still runs and says so.
    * The checker intentionally avoids judging voice, English density, and
      quality. Those require human or model review against the intended brief.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
RULES_PATH = SKILL_DIR / "assets" / "lint-rules.json"

# --------------------------------------------------------------------------
# Unicode classes
# --------------------------------------------------------------------------

MM_BLOCKS = (
    (0x1000, 0x109F),   # Myanmar
    (0x116D0, 0x116FF), # Myanmar Extended-A
    (0x11800, 0x1184F), # Myanmar Extended-B
    (0x11A00, 0x11A4F), # Myanmar Extended-C
)

# Base letters occupy their own cell and can end a word.
MM_BASE = set(range(0x1000, 0x102D)) | {0x1031, 0x103F} | set(range(0x1050, 0x1056)) \
    | set(range(0x105A, 0x105E)) | {0x1061, 0x1065, 0x1066, 0x106E, 0x106F, 0x1070} \
    | set(range(0x1075, 0x1082)) | {0x1084}

# Combining signs attach to the preceding base letter and are zero width.
MM_SIGN = set(range(0x102D, 0x1031)) | {0x1032, 0x1033, 0x1034, 0x1035, 0x1036,
                                       0x1037, 0x1038, 0x1039, 0x103A, 0x103B,
                                       0x103C, 0x103D, 0x103E} \
    | set(range(0x1056, 0x105A)) | {0x1062, 0x1063, 0x1064, 0x1067, 0x1069, 0x106A,
                                   0x106B, 0x106C, 0x106D, 0x1071, 0x1072, 0x1073,
                                   0x1074, 0x1082, 0x1083} | set(range(0x1068, 0x1069))

MM_DIGIT = set(range(0x1040, 0x104A))
MM_PUNCT = set(range(0x104A, 0x1050)) | {0x1037, 0x1038}

BURMESE_DANDA = "။"          # full stop
BURMESE_SECTION = "၊"        # pause / clause separator
BURMESE_VISARGA = "း"        # visarga, forms ။း question mark
BURMESE_DIGITS = "၀၁၂၃၄၅၆၇၈၉"

# The Zawgyi detector is a character-bigram model. Under roughly 40
# characters of Burmese context it answers "Unicode" for everything,
# including Zawgyi, so passages are windowed before being judged.
MIN_WINDOW_CHARS = 40
MIN_DOC_CHARS = 30

MM_RUN_RE = re.compile(
    "["
    "က-႟\U000116D0-\U000116FF"
    "\U00011800-\U0001184F\U00011A00-\U00011A4F"
    "]+"
)

EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF"
    "☀-➿⬀-⯿️‍⃣™ℹ]"
)
LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_'\-]*")
BURMESE_CLUSTER_RE = re.compile(
    "["
    "က-႟\U000116D0-\U000116FF"
    "\U00011800-\U0001184F\U00011A00-\U00011A4F"
    "]+"
)
def is_burmese(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in MM_BLOCKS)


def is_mm_base(cp: int) -> bool:
    return cp in MM_BASE


def is_mm_sign(cp: int) -> bool:
    return cp in MM_SIGN


def is_mm_digit(cp: int) -> bool:
    return cp in MM_DIGIT


def is_mm_punct(cp: int) -> bool:
    return cp in MM_PUNCT


# --------------------------------------------------------------------------
# Zawgyi detection
# --------------------------------------------------------------------------


class ZawgyiDetector:
    """Wraps `myanmartools` when available, falls back to a weak heuristic."""

    def __init__(self) -> None:
        self._detector = None
        self.available = False
        self.exact = False
        self.reason = ""
        try:
            from myanmartools import ZawgyiDetector as _D  # type: ignore

            self._detector = _D()
            self.available = True
            self.exact = True
        except Exception as exc:  # pragma: no cover - environment dependent
            self.reason = str(exc)

    def probability(self, text: str):
        """Return P(Zawgyi) in [0, 1], or None when it cannot be judged."""
        if self._detector is None:
            return self._heuristic(text)
        try:
            value = self._detector.get_zawgyi_probability(text)
        except Exception:
            return self._heuristic(text)
        if value == float("-inf"):
            return None
        return value

    @staticmethod
    def _heuristic(text: str):
        """Weak fallback: Zawgyi leans on U+1064 (KE PHO tone mark).

        U+103C (MEDIAL RA) and U+1039 (VIRAMA) are deliberately NOT used as
        signals — both appear in ordinary Unicode Burmese, so weighting them
        produces false positives on clean text. U+1064 is rare in standard
        Unicode Burmese and common in Zawgyi, so it is the only usable hint.

        Returns a value that the caller must treat as a hint, not a verdict.
        """
        if not any(is_burmese(ord(c)) for c in text):
            return None
        if any(ord(c) == 0x1064 for c in text):
            return 0.6
        return 0.0


# --------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------

ERROR = "error"
WARN = "warn"
INFO = "info"


@dataclass
class Finding:
    id: str
    severity: str
    line: int
    message: str
    snippet: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------
# Validator
# --------------------------------------------------------------------------


class Validator:
    def __init__(self, rules: dict, register: str, fmt: str, detector: ZawgyiDetector):
        self.rules = rules
        self.register = register
        self.fmt = fmt
        self.detector = detector
        self.reg = rules["registers"][register]
        self.findings: list[Finding] = []
        self._seen: set[tuple] = set()

    # -- helpers ---------------------------------------------------------

    def add(self, fid: str, severity: str, line: int, message: str, snippet: str = "") -> None:
        key = (fid, line, snippet.strip()[:40])
        if key in self._seen:
            return
        self._seen.add(key)
        self.findings.append(Finding(fid, severity, line, message, snippet.strip()[:120]))

    @staticmethod
    def _clip(line: str, start: int, end: int) -> str:
        return line[start:end]

    # -- checks ----------------------------------------------------------

    def check_encoding(self, lines: list[str]) -> None:
        """ENC-001/002/003 — Zawgyi detection.

        The detector is a character-bigram model, so it needs roughly 40
        characters of Burmese context before its verdict is meaningful.
        Below that it silently answers "Unicode". The document is therefore
        sliced into windows of contiguous Myanmar runs, and each window is
        judged on its own.
        """
        tokens = list(self._myanmar_tokens(lines))
        total = sum(len(t) for _, t in tokens)
        if total < MIN_DOC_CHARS:
            self.add(
                "ENC-003", INFO, 0,
                f"Only {total} characters of Burmese text — too little to "
                "judge the encoding. Check it by eye.",
            )
            return

        windows: list[list[tuple[int, str]]] = []
        current: list[tuple[int, str]] = []
        size = 0
        for line_no, token in tokens:
            current.append((line_no, token))
            size += len(token)
            if size >= MIN_WINDOW_CHARS:
                windows.append(current)
                current = []
                size = 0
        if current:
            if windows and size < MIN_WINDOW_CHARS // 2:
                windows[-1].extend(current)
            else:
                windows.append(current)

        exact = self.detector.exact
        severity = ERROR if exact else WARN
        zawgyi_lines: dict[int, tuple[float, str]] = {}
        ambiguous_lines: dict[int, tuple[float, str]] = {}
        unicode_lines: set[int] = set()

        for window in windows:
            text = " ".join(t for _, t in window)
            p = self.detector.probability(text)
            if p is None:
                continue
            first_line = window[0][0]
            joined = " ".join(t for _, t in window)[:120]
            if p >= 0.5:
                zawgyi_lines.setdefault(first_line, (p, joined))
            elif p > 0.1:
                ambiguous_lines.setdefault(first_line, (p, joined))
            else:
                unicode_lines.add(first_line)

        if zawgyi_lines and not unicode_lines:
            # The whole document is one encoding problem, not many.
            line, (p, joined) = min(zawgyi_lines.items())
            self.add(
                "ENC-001", severity, 0,
                f"The document looks like Zawgyi encoding (P={p:.2f}). "
                "Output must be Unicode Myanmar Script."
                + ("" if exact else " Heuristic detection — verify by hand."),
                joined,
            )
        else:
            for line, (p, joined) in sorted(zawgyi_lines.items()):
                self.add(
                    "ENC-001", severity, line,
                    f"This passage looks like Zawgyi encoding (P={p:.2f}). "
                    "Output must be Unicode Myanmar Script."
                    + ("" if exact else " Heuristic detection — verify by hand."),
                    joined,
                )
            if zawgyi_lines and unicode_lines:
                self.add(
                    "ENC-002", severity, 0,
                    "Document mixes Zawgyi and Unicode passages. Normalise "
                    "everything to Unicode.",
                )

        for line, (p, joined) in sorted(ambiguous_lines.items()):
            self.add(
                "ENC-003", WARN, line,
                f"Encoding is ambiguous (P={p:.2f}). Check this passage by "
                "hand.",
                joined,
            )

    @staticmethod
    def _myanmar_tokens(lines: list[str]):
        """Yield (line_no, token) for maximal runs of Myanmar-script chars."""
        for idx, line in enumerate(lines, start=1):
            for m in re.finditer(MM_RUN_RE, line):
                yield idx, m.group(0)

    def check_mix(self, lines: list[str], text: str) -> None:
        """MIX-002/003 — potentially broken script or word boundaries."""
        for idx, line in enumerate(lines, start=1):
            for m in re.finditer(
                r"(?<=[\u1000-\u109F\u116D0-\u116FF\u11800-\u1184F\u11A00-\u11A4F])"
                r"[A-Za-z]|[A-Za-z](?=[\u1000-\u109F\u116D0-\u116FF"
                r"\u11800-\u1184F\u11A00-\u11A4F])",
                line,
            ):
                if m.group(0)[0].isalpha() and ord(m.group(0)[0]) < 128:
                    # Latin run starts here. Look left past combining signs to
                    # the nearest base character.
                    pos = m.start() - 1
                    while pos >= 0 and is_mm_sign(ord(line[pos])):
                        pos -= 1
                    left_ok = pos < 0 or not is_mm_base(ord(line[pos]))
                else:
                    # Latin run ends here. Look right past combining signs.
                    pos = m.end()
                    while pos < len(line) and is_mm_sign(ord(line[pos])):
                        pos += 1
                    left_ok = pos >= len(line) or not is_mm_base(ord(line[pos]))
                if left_ok:
                    continue
                self.add(
                    "MIX-002", WARN, idx,
                    "Burmese and English touch with no space. Check whether a "
                    "space would make the script boundary easier to read.",
                    line,
                )
                break

            for m in re.finditer(r"(?<![A-Za-z])([A-Za-z]) (?=[A-Za-z])", line):
                if m.group(1) in ("a", "A", "i", "I"):
                    continue
                # "win's vlog" is an apostrophe, not a split word.
                if m.start() > 0 and line[m.start() - 1] == "'":
                    continue
                self.add(
                    "MIX-003", WARN, idx,
                    f"Possible split English word: '{m.group(1)}' standing alone.",
                    line,
                )
                break

    def check_punctuation(self, lines: list[str]) -> None:
        """PUN-001..005 — Burmese punctuation and whitespace."""
        ascii_sev = self.reg["ascii_terminal"]
        for idx, line in enumerate(lines, start=1):
            for m in re.finditer(
                r"[\u1000-\u109F\u116D0-\u116FF\u11800-\u1184F\u11A00-\u11A4F]"
                r"[ \t]*[.!?](?=[ \t]|$)",
                line,
            ):
                ch = m.group(0)[-1]
                if ch == ".":
                    self.add(
                        "PUN-001", ascii_sev, idx,
                        "ASCII '.' ends a Burmese sentence. Use '။'.",
                        line,
                    )
                else:
                    # '?' and '!' after Burmese are a real pattern in question
                    # headings ("ဘယ်လောက်ရနိုင်လဲ?"), so this is advice
                    # rather than a defect.
                    self.add(
                        "PUN-002", INFO, idx,
                        f"ASCII '{ch}' ends a Burmese sentence. '။း' is the "
                        "full form; '?' is a normal house style in short "
                        "question headings.",
                        line,
                    )
                break
            if re.search(r"[ \t]" + re.escape(BURMESE_DANDA), line):
                self.add(
                    "PUN-003", ERROR, idx,
                    "Space before '။'. Burmese punctuation attaches to the "
                    "preceding word.",
                    line,
                )
            if re.search(r"[ \t]{2,}", line):
                # "Label  :  Value" pads the spaces on purpose to line the
                # values up in a column. Skip double spaces next to a colon.
                padded = False
                for m in re.finditer(r"[ \t]{2,}", line):
                    lo = max(0, m.start() - 2)
                    hi = min(len(line), m.end() + 2)
                    if ":" in line[lo:hi] or "：" in line[lo:hi]:
                        padded = True
                        break
                if not padded:
                    self.add("PUN-004", WARN, idx, "Double space.", line)
            if line != line.rstrip():
                self.add("PUN-005", WARN, idx, "Trailing whitespace.", line)

    def check_numbers(self, lines: list[str]) -> None:
        """NUM-001/002 — digit consistency."""
        for idx, line in enumerate(lines, start=1):
            has_ascii = bool(re.search(r"[0-9]", line))
            has_burmese = any(c in BURMESE_DIGITS for c in line)
            if has_ascii and has_burmese:
                # Mixing is normal when a line carries two different kinds of
                # value, e.g. "S$2,800 ... ၆%" or "24 Oct 2026 ... ၂ နာရီ".
                self.add(
                    "NUM-001", INFO, idx,
                    "Arabic and Burmese digits on the same line. Fine when the "
                    "values differ in kind (currency, date, time); check it.",
                    line,
                )
            if has_burmese and re.search(
                r"[\u1040-\u1049]+\s*(KB|MB|GB|TB|KBps|ms|px)\b", line
            ):
                self.add(
                    "NUM-002", WARN, idx,
                    "Burmese digits used for a technical value. Use Arabic "
                    "digits for versions, ports, and sizes.",
                    line,
                )

    def check_register_terms(self, lines: list[str]) -> None:
        """REG-001 — words that belong to another register."""
        forbidden = self.reg.get("forbid_terms", [])
        if not forbidden:
            return
        for idx, line in enumerate(lines, start=1):
            for term in forbidden:
                if term in line:
                    self.add(
                        "REG-001", WARN, idx,
                        f"'{term}' does not fit the {self.register} register.",
                        line,
                    )
                    break

    def check_style(self, lines: list[str], text: str) -> None:
        """STY-001..004 — banned phrases, overused connectives, placeholders."""
        for idx, line in enumerate(lines, start=1):
            for phrase in self.rules.get("banned_phrases", []):
                if phrase in line:
                    self.add(
                        "STY-001", ERROR, idx,
                        f"Banned phrase: '{phrase}'.",
                        line,
                    )
                    break
            for bad in self.rules.get("avoid_transliterations", []):
                if bad in line:
                    self.add(
                        "STY-004", WARN, idx,
                        f"'{bad}' is a transliteration nobody uses. Keep the "
                        "English term.",
                        line,
                    )
                    break
            for pattern in self.rules.get("awkward_phrases", []):
                rx, error = compile_pattern(pattern)
                if error is not None:
                    self.add(
                        "CFG-001", WARN, idx,
                        f"Rule pattern is not a valid regex ({error}); it was "
                        f"matched literally: /{pattern}/",
                    )
                if rx.search(line):
                    self.add(
                        "STY-005", WARN, idx,
                        f"Awkward phrasing matching /{pattern}/.",
                        line,
                    )
                    break

        for rule in self.rules.get("overused", []):
            term = rule["term"]
            count = text.count(term)
            if count > rule["max"]:
                self.add(
                    "STY-002", WARN, 0,
                    f"'{term}' appears {count} times (max {rule['max']}). "
                    "Vary the connectives.",
                )

        for idx, line in enumerate(lines, start=1):
            for ph in self.rules.get("placeholders", []):
                if ph in line:
                    self.add(
                        "STY-003", ERROR, idx,
                        f"Unresolved placeholder: '{ph}'.",
                        line,
                    )
                    break

    def check_length(self, lines: list[str], text: str) -> None:
        """LEN-001..004 — length targets and limits."""
        max_words = self.reg["max_sentence_words"]
        for idx, line in enumerate(lines, start=1):
            for sentence in split_sentences(line):
                units = count_units(sentence)
                if units > max_words:
                    self.add(
                        "LEN-001", WARN, idx,
                        f"Sentence is {units} units (max {max_words} for "
                        f"{self.register}).",
                        sentence,
                    )
                    break

        spec = self.rules["formats"].get(self.fmt, {})
        units = count_units(text)
        band = spec.get("units")
        if band:
            lo, hi = band
            if units < lo:
                self.add(
                    "LEN-002", WARN, 0,
                    f"Content is {units} units, below the {self.fmt} target of "
                    f"{lo}-{hi}.",
                )
            elif units > hi:
                self.add(
                    "LEN-002", WARN, 0,
                    f"Content is {units} units, above the {self.fmt} target of "
                    f"{lo}-{hi}.",
                )
        max_chars = spec.get("max_chars")
        if max_chars and len(text) > max_chars:
            self.add(
                "LEN-003", ERROR, 0,
                f"Content is {len(text)} characters, over the {self.fmt} limit "
                f"of {max_chars}.",
            )
        title_max = spec.get("title_chars")
        if title_max:
            for line in lines:
                if line.startswith("# "):
                    title = line[2:].strip()
                    if len(title) > title_max:
                        self.add(
                            "LEN-004", WARN, 1,
                            f"Title is {len(title)} characters (max "
                            f"{title_max}).",
                            title,
                        )
                    break

    def check_emoji(self, lines: list[str], text: str) -> None:
        """EMO-001/002 — emoji budget, measured as density.

        A fixed count is unreliable because a document may hold several posts.
        Density per 100 word-units is stable across post lengths.
        """
        count = sum(len(EMOJI_RE.findall(line)) for line in lines)
        units = max(count_units(text), 1)
        per_100 = count * 100.0 / units
        limit = self.reg.get("max_emoji_per_100", 25)
        if per_100 > limit:
            self.add(
                "EMO-001", WARN, 0,
                f"{count} emoji in {units} units "
                f"({per_100:.1f} per 100 units, over the {self.register} limit "
                f"of {limit}).",
            )
        if not self.reg.get("allow_emoji", True) and count:
            self.add(
                "EMO-002", WARN, 0,
                f"{self.register} register should not use emoji ({count} "
                "found).",
            )

    # -- driver ----------------------------------------------------------

    def run(self, text: str) -> list[Finding]:
        lines = text.splitlines()
        self.check_encoding(lines)
        self.check_mix(lines, text)
        self.check_punctuation(lines)
        self.check_numbers(lines)
        self.check_register_terms(lines)
        self.check_style(lines, text)
        self.check_length(lines, text)
        self.check_emoji(lines, text)
        self.findings.sort(key=lambda f: (f.line, f.id))
        return self.findings


# --------------------------------------------------------------------------
# Text metrics
# --------------------------------------------------------------------------


def is_burmese_dominant(text: str) -> bool:
    latin = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    burmese = sum(1 for c in text if is_mm_base(ord(c)))
    return burmese > 0 and burmese >= latin


_PATTERN_CACHE: dict[str, tuple[re.Pattern, str | None]] = {}


def compile_pattern(pattern: str) -> tuple[re.Pattern, str | None]:
    """Compile a rule pattern.

    Returns (pattern, error). When the pattern is not a valid regex it is
    treated as a literal string, and the error is reported so a broken rule
    is visible instead of silently never matching.
    """
    cached = _PATTERN_CACHE.get(pattern)
    if cached is not None:
        return cached
    try:
        compiled = re.compile(pattern)
        error = None
    except re.error as exc:
        compiled = re.compile(re.escape(pattern))
        error = str(exc)
    _PATTERN_CACHE[pattern] = (compiled, error)
    return compiled, error


def count_units(text: str) -> int:
    """Approximate word count.

    Burmese does not separate words with spaces, so whitespace tokens would
    badly undercount. Instead count Latin words plus Burmese syllable
    clusters, which tracks length proportionally.
    """
    total = len(LATIN_WORD_RE.findall(text))
    for cluster in BURMESE_CLUSTER_RE.findall(text):
        n = 0
        for ch in cluster:
            cp = ord(ch)
            if is_mm_base(cp):
                n += 1
            elif is_mm_sign(cp) and n == 0:
                n += 1
        total += n
    return total


_SENT_SPLIT_RE = re.compile(
    r"(?:[။။း၊]|(?<=[A-Za-z0-9])\.(?=\s|$)|[!?](?=\s|$)|\n)"
)


def split_sentences(line: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT_RE.split(line) if s and s.strip()]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def load_rules() -> dict:
    try:
        return json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: rules file not found at {RULES_PATH}", file=sys.stderr)
        raise SystemExit(2)
    except json.JSONDecodeError as exc:
        print(f"error: rules file is not valid JSON: {exc}", file=sys.stderr)
        raise SystemExit(2)


def read_input(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: no such file: {path}", file=sys.stderr)
        raise SystemExit(2)
    except UnicodeDecodeError:
        print(
            f"error: {path} is not valid UTF-8. If this is Zawgyi it must be "
            "converted to Unicode before validation.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="validate.py",
        description="Check objective mechanical issues in Burmese content.",
    )
    ap.add_argument("path", help="file to validate, or - for stdin")
    ap.add_argument(
        "--register", default="professional",
        help="professional | casual | formal | diaspora (default: professional)",
    )
    ap.add_argument(
        "--format", default="generic",
        help=(
            "content format key: facebook | web | blog | generic "
            "(legacy aliases are also accepted; default: generic)"
        ),
    )
    ap.add_argument("--json", action="store_true", help="emit JSON findings")
    ap.add_argument(
        "--strict", action="store_true", help="treat warnings as errors"
    )
    ap.add_argument("--quiet", action="store_true", help="suppress warnings")
    args = ap.parse_args(argv)

    rules = load_rules()
    if args.register not in rules["registers"]:
        print(
            f"error: unknown register '{args.register}'. "
            f"Choose from: {', '.join(rules['registers'])}",
            file=sys.stderr,
        )
        return 2
    if args.format not in rules["formats"]:
        print(
            f"error: unknown format '{args.format}'. "
            f"Choose from: {', '.join(rules['formats'])}",
            file=sys.stderr,
        )
        return 2

    text = read_input(args.path)
    detector = ZawgyiDetector()
    validator = Validator(rules, args.register, args.format, detector)
    findings = validator.run(text)

    errors = [f for f in findings if f.severity == ERROR]
    all_warns = [f for f in findings if f.severity == WARN]
    shown_warns = [] if args.quiet else all_warns

    if args.json:
        print(
            json.dumps(
                {
                    "file": args.path,
                    "register": args.register,
                    "format": args.format,
                    "zawgyi_detector_available": detector.available,
                    "errors": len(errors),
                    "warnings": len(all_warns),
                    "findings": [f.to_dict() for f in findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if not detector.available:
            print(
                "note: myanmartools is not installed, so Zawgyi detection is "
                "heuristic only. Install with: pip install -r "
                f"{SKILL_DIR / 'scripts' / 'requirements.txt'}",
                file=sys.stderr,
            )
        for f in findings:
            if f.severity == WARN and args.quiet:
                continue
            where = f"line {f.line}" if f.line else "document"
            print(f"[{f.severity.upper():5}] {f.id}  {where}: {f.message}")
            if f.snippet:
                print(f"        | {f.snippet}")
        print(
            f"\n{len(errors)} error(s), {len(shown_warns)} warning(s) "
            f"[register={args.register}, format={args.format}]"
        )

    if errors:
        return 1
    if args.strict and all_warns:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
