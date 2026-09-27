"""Meaningful offline checks for grounded extraction and missing fields."""

from extractor import extract


def main() -> None:
    result = extract("Published: 2 September 2026\nApplication deadline: 15 October 2026\n"
                     "Required documents: CV and transcript\nPlease apply online.")
    assert [x.normalized_date for x in result["deadlines"]] == ["2026-10-15"]
    assert result["deadlines"][0].evidence == "Application deadline: 15 October 2026"
    assert len(result["documents"]) == len(result["actions"]) == 1

    bn = extract("প্রকাশ: ১০ সেপ্টেম্বর ২০২৬\nআবেদনের শেষ তারিখ: ১৫ অক্টোবর ২০২৬\n"
                 "প্রয়োজনীয় কাগজপত্র: জীবনবৃত্তান্ত এবং সনদ")
    assert [x.normalized_date for x in bn["deadlines"]] == ["2026-10-15"]
    assert len(bn["documents"]) == 1

    missing = extract("The schedule for the next semester is now available.")
    assert all(not values for values in missing.values())
    assert not extract("Application deadline not announced: 15 October 2026")["deadlines"]
    assert not extract("Closing date 31 February 2026")["deadlines"]
    print("Extractor checks passed")


if __name__ == "__main__":
    main()
