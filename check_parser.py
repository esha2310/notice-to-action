"""Offline behavior checks: dates must keep their role and findings need source lines."""

from notice_parser import parse_notice


def main() -> None:
    university = parse_notice(
        "Published date: 2 March 2026\n"
        "Students can submit the signed application with an admit card before the "
        "application deadline: 04 March 2026.\n"
        "The exam will be held on 08 March 2026.\n"
        "New students do not require self-registration.",
        "University notice",
    )
    dates = university["dates"]
    assert [x.normalized_date for x in dates["Publication date"]] == ["2026-03-02"]
    assert [x.normalized_date for x in dates["Deadline (verify purpose)"]] == ["2026-03-04"]
    assert [x.normalized_date for x in dates["Event / exam / registration date"]] == ["2026-03-08"]
    assert any("do not require" in x.source for x in university["fields"]["Audience / eligibility"])

    scholarship = parse_notice(
        "The scholarship supports tuition of eligible postgraduate students.\n"
        "Applicants must have a degree and meet the language requirement.\n"
        "Deadlines vary by university; apply following that university website.",
        "Scholarship",
    )
    assert not scholarship["dates"]["Deadline (verify purpose)"]
    assert scholarship["fields"]["Funding stated"]

    job = parse_notice(
        "Position: Research Assistant\n"
        "Education and experience requirements: degree and two years of experience.\n"
        "Send CV and cover letter by email; mention the position in the subject line.\n"
        "Application deadline:\n23 April 2026\n"
        "Interview date: 30 April 2026.",
        "Job circular",
    )
    assert [x.normalized_date for x in job["dates"]["Deadline (verify purpose)"]] == ["2026-04-23"]
    assert [x.normalized_date for x in job["dates"]["Event / exam / registration date"]] == ["2026-04-30"]
    assert any("CV" in x.source for x in job["fields"]["Documents"])
    assert all(x.line_number > 0 and x.source for bucket in job["fields"].values() for x in bucket)

    poster = parse_notice(
        "Company: Mercury Medical Ltd\nPosition: Data Entry Executive\n"
        "Deadline:\n21 February 2026\nSalary: 20000 - 22000",
        "Job circular",
    )
    assert [x.normalized_date for x in poster["dates"]["Deadline (verify purpose)"]] == ["2026-02-21"]
    assert any("Data Entry Executive" in x.source for x in poster["fields"]["Position / employer"])

    bn = parse_notice(
        "প্রকাশের তারিখ: ২০ সেপ্টেম্বর ২০২৬\n"
        "আবেদনের শেষ তারিখ: ৩০ সেপ্টেম্বর ২০২৬\n"
        "জীবনবৃত্তান্ত ও শিক্ষাগত সনদ ডাকযোগে জমা দিতে হবে।",
        "Job circular",
    )
    assert [x.normalized_date for x in bn["dates"]["Publication date"]] == ["2026-09-20"]
    assert [x.normalized_date for x in bn["dates"]["Deadline (verify purpose)"]] == ["2026-09-30"]
    assert bn["fields"]["Documents"]

    other = parse_notice(
        "রিভিউ আবেদন সংক্রান্ত বিজ্ঞপ্তি\n"
        "আবেদন ফি জমা করার সর্বশেষ সময়ঃ ০১-১১-২০২৫ রাত ১১:৫৯।\n"
        "পেমেন্ট পদ্ধতি SMS; ফলাফল অফিসিয়াল ওয়েবসাইটে প্রকাশ হবে।",
        "Other notice",
    )
    assert [x.normalized_date for x in other["dates"]["Deadline (verify purpose)"]] == ["2025-11-01"]
    assert other["fields"]["Payment / fee if stated"]

    absence = parse_notice("A new opportunity is announced; further details will follow.", "Job circular")
    assert not any(absence["dates"].values())
    print("Category and evidence checks passed")


if __name__ == "__main__":
    main()
