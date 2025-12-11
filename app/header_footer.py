from collections import Counter
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class HeaderFooterPatterns:
    header_lines: List[str]
    footer_lines: List[str]


def _split_lines_per_page(pages_text: List[str]) -> List[List[str]]:
    return [page.splitlines() for page in pages_text]


def detect_header_footer(pages_text: List[str], min_occurrences: int = 3) -> HeaderFooterPatterns:
    """
    Sehr einfache Heuristik:
    - Wiederkehrende erste Zeilen über mehrere Seiten => Header
    - Wiederkehrende letzte Zeilen über mehrere Seiten => Footer
    """
    pages_lines = _split_lines_per_page(pages_text)

    first_lines = [lines[0].strip() for lines in pages_lines if lines]
    last_lines = [lines[-1].strip() for lines in pages_lines if lines]

    header_counts = Counter([l for l in first_lines if l])
    footer_counts = Counter([l for l in last_lines if l])

    header_lines = [line for line, cnt in header_counts.items() if cnt >= min_occurrences]
    footer_lines = [line for line, cnt in footer_counts.items() if cnt >= min_occurrences]

    return HeaderFooterPatterns(header_lines=header_lines, footer_lines=footer_lines)


def remove_headers_footers(pages_text: List[str]) -> List[str]:
    """
    Entfernt erkannte Header-/Footer-Zeilen aus den Seiten.
    """
    patterns = detect_header_footer(pages_text)
    pages_lines = _split_lines_per_page(pages_text)

    cleaned_pages: List[str] = []
    for lines in pages_lines:
        cleaned = []
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if idx == 0 and stripped in patterns.header_lines:
                continue
            if idx == len(lines) - 1 and stripped in patterns.footer_lines:
                continue
            cleaned.append(line)
        cleaned_pages.append("\n".join(cleaned))

    return cleaned_pages


