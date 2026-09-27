"""Conservative, category-specific evidence lines from pasted or extracted notices.

This module does not decide eligibility or validate that a notice is genuine.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from extractor import _parse_dates


@dataclass(frozen=True)
class Evidence:
    text: str
    source: str
    line_number: int
    normalized_date: str = ""


CATEGORIES = ("University notice", "Scholarship", "Job circular", "Other notice")

# Fields are potential information to look for, not mandatory notice contents.
FIELDS = {
    "Other notice": {
        "Subject / affected people": r"\b(?:notice|review|recheck|applicants?|candidates?|results?|examination)\b|বিজ্ঞপ্তি|রিভিউ|পুনঃনিরীক্ষ|আবেদনকারী|প্রার্থী|ফলাফল|পরীক্ষা",
        "Action / submission": r"\b(?:apply|submit|review application|send|online|sms|payment method)\b|আবেদন|জমা|দাখিল|প্রেরণ|মোবাইল|এসএমএস|পেমেন্ট",
        "Payment / fee if stated": r"\b(?:fee|payment|pay|taka|tk)\b|ফি|টাকা|পেমেন্ট|পরিশোধ|কর্তন",
        "Outcome / further information": r"\b(?:result|website|will be published|contact|office)\b|ফলাফল|ওয়েবসাইট|ওয়েবসাইট|প্রকাশ|অফিস|যোগাযোগ",
    },
    "University notice": {
        "Audience / eligibility": r"\b(?:students?|undergraduate|postgraduate|eligible|department|faculty|semester|batch|credits?|exempt|do not require)\b|শিক্ষার্থী|বিভাগ|শিক্ষাবর্ষ|সেমিস্টার|যোগ্য|প্রযোজ্য|অব্যাহতি",
        "What to do": r"\b(?:submit|register|registration|apply|complete|attend|collect|sign(?:ed)?|bring|report to|fill (?:in|out))\b|আবেদন|জমা|দাখিল|নিবন্ধন|রেজিস্ট্রেশন|উপস্থিত|স্বাক্ষর|পূরণ",
        "Supporting documents": r"\b(?:documents?|certificate|admit card|application form|transcript|supporting evidence)\b|কাগজপত্র|সনদ|প্রবেশপত্র|স্বাক্ষরিত|সংযুক্তি",
        "Place / channel": r"\b(?:office|room|venue|campus|online|portal|website|email|e-mail|link)\b|অফিস|কক্ষ|স্থান|অনলাইনে|ইমেইল|ওয়েবসাইট|ওয়েবসাইট",
    },
    "Scholarship": {
        "Programme / study level": r"\b(?:scholarship|fellowship|undergraduate|postgraduate|masters?|phd|doctoral|programme|program|course)\b|বৃত্তি|স্কলারশিপ|স্নাতক|স্নাতকোত্তর|ডক্টরাল|পিএইচডি",
        "Eligibility / conditions": r"\b(?:eligible|eligibility|citizenship|citizen|nationality|degree|gpa|cgpa|language requirement|must have|must be|criteria)\b|যোগ্যতা|শর্ত|নাগরিক|ন্যূনতম|সিজিপিএ",
        "Funding stated": r"\b(?:tuition|stipend|allowance|funding|funded|waiver|insurance|accommodation|scholarship (?:is )?worth)\b|টিউশন|বেতন|ভাতা|অর্থায়ন|অর্থায়ন|আবাসন|বীমা",
        "Documents": r"\b(?:cv|resume|transcript|recommendation|reference letter|certificate|statement of purpose|passport|documents?)\b|জীবনবৃত্তান্ত|কাগজপত্র|সনদ|পাসপোর্ট|সুপারিশ",
        "How to apply": r"\b(?:apply|application|submit|form|portal|website|nomination|nominat(?:e|ion))\b|আবেদন|মনোনয়ন|মনোনয়ন|জমা|ফর্ম|ফরম",
    },
    "Job circular": {
        "Position / employer": r"\b(?:position|post|vacancy|recruitment|job title|employer|organisation|organization|company|officer|associate|assistant)\b|পদ|পদের|নিয়োগ|নিয়োগ|প্রতিষ্ঠান",
        "Eligibility / experience": r"\b(?:qualification|degree|education|experience|skills?|eligible|age limit|must have|years? of experience)\b|যোগ্যতা|অভিজ্ঞতা|বয়স|বয়স|শিক্ষাগত|দক্ষতা",
        "Pay / benefits if stated": r"\b(?:salary|pay scale|compensation|benefits?|remuneration|monthly pay)\b|বেতন|বেতনস্কেল|সুবিধা|সম্মানী",
        "Documents": r"\b(?:cv|resume|cover letter|motivation letter|transcript|certificate|photograph|passport|nid|references?)\b|জীবনবৃত্তান্ত|কাগজপত্র|সনদ|জাতীয় পরিচয়পত্র|জাতীয় পরিচয়পত্র|ছবি",
        "Application method / fee": r"\b(?:apply|application|submit|send|email|e-mail|portal|fee|subject line|address)\b|আবেদন|জমা|পাঠাতে|ইমেইল|ফি|ঠিকানা",
        "Workplace / next step": r"\b(?:location|workplace|place of posting|interview|shortlisted|admit card|written test)\b|কর্মস্থল|কর্মস্থলে|সাক্ষাৎকার|পরীক্ষা|প্রবেশপত্র",
    },
}

DATE_CUES = {
    "Deadline (verify purpose)": re.compile(
        r"\b(?:application deadline|deadline (?:for |of )?(?:application|submission|registration)|"
        r"before (?:the )?deadline (?:of|on|by)|apply deadline|"
        r"last date (?:to|for|of)|closing date|applications? close|apply by|submit by|"
        r"registration deadline|deadline to apply|application ends?)\b|(?<!\w)deadline\s*[:：]|"
        r"আবেদনের?\s*শেষ\s*তারিখ|আবেদনের?\s*সময়সীমা|আবেদনের?\s*সময়সীমা|"
        r"জমা\s*দেওয়ার\s*শেষ|জমা\s*দেওয়ার\s*শেষ|রেজিস্ট্রেশনের\s*শেষ|"
        r"(?:আবেদন|ফি).{0,45}?(?:সর্বশেষ\s*সম[য়য়]|শেষ\s*সম[য়য়])|সর্বশেষ\s*সম[য়য়]\s*[:ঃ]", re.I),
    "Event / exam / registration date": re.compile(
        r"\b(?:exam(?:ination)? (?:date|starts?|will be held)|event (?:date|starts?)|"
        r"interview (?:date|will be held)|registration (?:opens?|starts?|will be held)|"
        r"classes? (?:begin|start)|will (?:be held|take place))\b|"
        r"পরীক্ষা\s*(?:শুরু|অনুষ্ঠিত)|পরীক্ষার\s*তারিখ|অনুষ্ঠিত\s*হবে|"
        r"শুরু\s*হবে|সাক্ষাৎকারের\s*তারিখ", re.I),
    "Publication date": re.compile(
        r"\b(?:publish(?:ed)? date|date of publication|notice date|issued on)\b|"
        r"প্রকাশের\s*তারিখ|প্রকাশিত\s*হয়েছে|প্রকাশিত\s*হয়েছে|স্মারক\s*নং", re.I),
}
NEGATIVE_DEADLINE = re.compile(
    r"\b(?:deadline (?:is )?not (?:yet )?(?:announced|available|stated)|"
    r"deadlines? (?:vary|varies|depend|differs))\b|"
    r"শেষ\s*তারিখ\s*(?:ঘোষণা\s*করা\s*হয়নি|ঘোষণা\s*করা\s*হয়নি)", re.I)


def parse_notice(text: str, category: str) -> dict[str, dict[str, list[Evidence]] | list[str]]:
    if category not in FIELDS:
        raise ValueError("Choose a supported notice category")
    if len(text) > 300_000:
        raise ValueError("Notice text exceeds the 300,000-character limit")
    lines = [(n, re.sub(r"\s+", " ", raw).strip()) for n, raw in enumerate(text.splitlines(), 1)]
    lines = [(n, line) for n, line in lines if line]
    fields = {label: [] for label in FIELDS[category]}
    dates = {label: [] for label in DATE_CUES}
    notes: list[str] = []
    for index, (n, line) in enumerate(lines):
        if "\ufffd" in line:
            notes.append("Unreadable characters were found; check the original image or PDF.")
        for label, pattern in FIELDS[category].items():
            if re.search(pattern, line, re.I) and len(fields[label]) < 8:
                fields[label].append(Evidence(line[:700], line[:700], n))
        for label, cue in DATE_CUES.items():
            if not cue.search(line):
                continue
            if label == "Deadline (verify purpose)" and NEGATIVE_DEADLINE.search(line):
                notes.append("A deadline is described as missing or varying; check the original notice.")
                continue
            found = _parse_dates(line)
            evidence = line
            # OCR often places a short date immediately after its heading.
            if not found and index + 1 < len(lines) and len(line) <= 105:
                next_n, next_line = lines[index + 1]
                if next_n <= n + 2 and len(next_line) <= 95 and not any(c.search(next_line) for c in DATE_CUES.values()):
                    found = _parse_dates(next_line)
                    evidence = f"{line} | {next_line}"
            for value, iso_date in found:
                item = Evidence(value, evidence[:700], n, iso_date)
                if item not in dates[label] and len(dates[label]) < 12:
                    dates[label].append(item)
    if not lines:
        notes.append("No readable notice text was found.")
    elif len(text.strip()) < 80:
        notes.append("Very little text was read. Results may be incomplete; compare the original notice.")
    if not any(dates.values()):
        notes.append("No clearly labelled full calendar date was extracted; this does not mean there is no date.")
    return {"fields": fields, "dates": dates, "notes": list(dict.fromkeys(notes))}
