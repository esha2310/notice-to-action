"""Conservative, source-grounded notice extraction; no network or paid model."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Finding:
    value: str
    evidence: str
    line_number: int
    normalized_date: str = ""


MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "জানুয়ারি": 1, "জানুয়ারি": 1, "ফেব্রুয়ারি": 2, "ফেব্রুয়ারি": 2,
    "মার্চ": 3, "এপ্রিল": 4, "মে": 5, "জুন": 6,
    "জুলাই": 7, "আগস্ট": 8, "সেপ্টেম্বর": 9, "অক্টোবর": 10,
    "নভেম্বর": 11, "ডিসেম্বর": 12,
}
MONTH_PATTERN = "|".join(sorted(map(re.escape, MONTHS), key=len, reverse=True))
DATE_PATTERN = re.compile(
    rf"(?<!\d)(\d{{1,2}})(?:st|nd|rd|th)?\s+({MONTH_PATTERN})\s*,?\s*(\d{{4}})(?!\d)"
    r"|(?<!\d)(\d{4})-(\d{1,2})-(\d{1,2})(?!\d)"
    r"|(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)",
    re.IGNORECASE,
)
DEADLINE_CUE = re.compile(
    r"\b(?:deadline|last date|last day|apply by|submit by|closing date|applications? close|"
    r"due date|application ends?)\b|শেষ\s*তারিখ|সর্বশেষ\s*তারিখ|আবেদনের\s*শেষ|"
    r"জমা\s*দেওয়ার\s*শেষ|জমা\s*দেয়ার\s*শেষ|জমা\s*দেবার\s*শেষ|সময়সীমা|সময়সীমা",
    re.IGNORECASE,
)
DOCUMENT_CUE = re.compile(
    r"\b(?:required documents?|documents? required|attach(?:ments?)?|enclose|"
    r"submit (?:the )?following documents?)\b|প্রয়োজনীয়\s*কাগজপত্র|"
    r"প্রয়োজনীয়\s*কাগজপত্র|সংযুক্ত\s*করতে|দাখিল\s*করতে\s*হবে",
    re.IGNORECASE,
)
ACTION_CUE = re.compile(
    r"\b(?:apply online|applications? are invited|submit (?:your|the|an) |"
    r"register (?:online|at|by)|fill (?:in|out) the form)\b|"
    r"আবেদন\s*করতে\s*হবে|আবেদন\s*করুন|আবেদন\s*আহ্বান|"
    r"ফরম\s*পূরণ|ফর্ম\s*পূরণ|জমা\s*দিতে\s*হবে",
    re.IGNORECASE,
)
NEGATIVE_CUE = re.compile(
    r"deadline (?:is )?not (?:yet )?(?:announced|available|stated)|"
    r"শেষ\s*তারিখ\s*(?:পরে|এখনও|ঘোষণা\s*করা\s*হয়নি)", re.IGNORECASE,
)


def _ascii_digits(text: str) -> str:
    return "".join(
        str(unicodedata.digit(c)) if c.isdigit() and not c.isascii() else c
        for c in text
    )


def _parse_dates(line: str) -> list[tuple[str, str]]:
    dates = []
    for match in DATE_PATTERN.finditer(_ascii_digits(line)):
        groups = match.groups()
        if groups[0]:
            day, month, year = int(groups[0]), MONTHS[groups[1].casefold()], int(groups[2])
        elif groups[3]:
            year, month, day = map(int, groups[3:6])
        else:
            day, month, year = map(int, groups[6:9])  # DD/MM/YYYY only where context is explicit
        try:
            parsed = date(year, month, day).isoformat()
        except ValueError:
            continue
        dates.append((match.group(0), parsed))
    return dates


def extract(text: str) -> dict[str, list[Finding]]:
    """Return only evidence-backed candidates. Empty lists mean 'not found'."""
    if len(text) > 300_000:
        raise ValueError("Notice text exceeds the 300,000-character limit")
    lines = [re.sub(r"\s+", " ", x).strip() for x in text.splitlines()]
    lines = [x for x in lines if x]
    out: dict[str, list[Finding]] = {"deadlines": [], "documents": [], "actions": []}
    for number, line in enumerate(lines, 1):
        evidence = line[:600]
        if DEADLINE_CUE.search(line) and not NEGATIVE_CUE.search(line):
            for value, normalized in _parse_dates(line):
                out["deadlines"].append(Finding(value, evidence, number, normalized))
        if DOCUMENT_CUE.search(line):
            out["documents"].append(Finding(evidence, evidence, number))
        if ACTION_CUE.search(line):
            out["actions"].append(Finding(evidence, evidence, number))
    return {key: list(dict.fromkeys(items))[:12] for key, items in out.items()}
