from typing import List

import fitz  # PyMuPDF

from .header_footer import remove_headers_footers
from .models import ExtractOptions, Page, PageParagraph


def _extract_page_texts(doc: "fitz.Document") -> List[str]:
    pages: List[str] = []
    for page in doc:
        text = page.get_text("text")
        pages.append(text or "")
    return pages


def _join_broken_lines(text: str) -> str:
    """
    Verbindet Zeilen, die mitten im Satz/Absatz umgebrochen wurden (PDF-Layout-Problem).
    
    Aggressive Strategie: Verbinde ALLE Zeilen außer wenn klar ein neuer Absatz beginnt.
    """
    import re
    
    lines = text.split("\n")
    if not lines:
        return text
    
    result = []
    
    # Muster für "hier beginnt definitiv ein neuer Absatz"
    new_paragraph_patterns = [
        r'^\s*$',                               # Leerzeile
        r'^\s*[•●○▪►▸■□–-]\s',                  # Bullet Points
        r'^\s*\d+[.)]\s',                       # Nummerierte Liste: "1." oder "1)"
        r'^\s*[a-z][.)]\s',                     # Alphabetische Liste: "a." oder "a)"
        r'^={3,}|^-{3,}|^_{3,}',               # Trennlinien
        r'^\s*©\s',                             # Copyright
        r'^\d{1,2}[-./]\d{1,2}[-./]\d{2,4}\s',  # Datum am Zeilenanfang
    ]
    new_para_regex = re.compile('|'.join(new_paragraph_patterns))
    
    # Muster für "Zeile endet mit echtem Satzende"
    # Satzzeichen gefolgt von optional Anführungszeichen/Klammern
    sentence_end = re.compile(r'[.!?]\s*[»"\')\]]*\s*$')
    
    # Muster für Überschriften (kurze Zeilen die alleinstehen sollten)
    # z.B. "Konfrontation – oder ein Neustart?"
    heading_pattern = re.compile(r'^[A-ZÄÖÜ«»„"].*[?!:]\s*$')
    
    i = 0
    while i < len(lines):
        current = lines[i].rstrip()
        
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            next_stripped = next_line.strip()
            
            # NICHT verbinden wenn:
            # 1. Aktuelle Zeile ist leer
            # 2. Nächste Zeile ist leer oder beginnt neuen Absatz
            # 3. Aktuelle Zeile endet mit Satzzeichen UND nächste beginnt mit Großbuchstaben
            # 4. Aktuelle Zeile ist eine Überschrift
            
            is_current_empty = not current
            is_next_new_para = not next_stripped or new_para_regex.match(next_stripped)
            is_sentence_end_and_new_sentence = (
                sentence_end.search(current) and 
                next_stripped and 
                next_stripped[0].isupper()
            )
            is_heading = heading_pattern.match(current) if current else False
            
            should_break = (
                is_current_empty or
                is_next_new_para or
                is_sentence_end_and_new_sentence or
                is_heading
            )
            
            if should_break:
                result.append(current + "\n")
            else:
                # Verbinden - prüfe ob Bindestrich-Trennung
                if current.endswith('-'):
                    # Wort-Trennung: "Rosen-\ngartenstrasse" → "Rosengartenstrasse"
                    result.append(current[:-1])
                else:
                    result.append(current + " ")
        else:
            result.append(current)
        
        i += 1
    
    return "".join(result).rstrip("\n")


def _normalize_whitespace(text: str) -> str:
    """Normalisiert Whitespace und verbindet gebrochene Zeilen."""
    import re

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    
    # Erst gebrochene Zeilen verbinden
    text = _join_broken_lines(text)
    
    # Dann mehrfache Leerzeichen reduzieren
    text = re.sub(r"[ \t]+", " ", text)
    # Mehrfach-Blankzeilen reduzieren
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_paragraphs(text: str) -> List[str]:
    # Splittet auf doppelte Zeilenumbrüche als grobe Paragraphen-Heuristik
    paragraphs = [p.strip() for p in text.split("\n\n")]
    return [p for p in paragraphs if p]


def extract_pdf(
    pdf_bytes: bytes,
    options: ExtractOptions,
) -> List[Page]:
    """
    Extrahiert Text aus einem PDF als Liste von Page-Objekten.
    """
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        raw_pages = _extract_page_texts(doc)

    if options.remove_headers_footers:
        raw_pages = remove_headers_footers(raw_pages)

    pages: List[Page] = []

    for i, page_text in enumerate(raw_pages):
        text = page_text
        if options.normalize_whitespace:
            text = _normalize_whitespace(text)

        paragraphs_text = _split_paragraphs(text) if options.mode == "paragraphs" else [text]
        paragraphs: List[PageParagraph] = [
            PageParagraph(index=idx, text=p) for idx, p in enumerate(paragraphs_text)
        ]

        pages.append(
            Page(
                page_number=i + 1,
                text=text,  # Immer Text behalten für full_text Zusammenführung
                paragraphs=paragraphs if options.mode == "paragraphs" else [],
            )
        )

    return pages


