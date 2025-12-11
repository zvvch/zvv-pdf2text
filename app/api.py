from typing import List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from fastapi.responses import PlainTextResponse

from .http_client import fetch_pdf_from_url
from .extractor import extract_pdf
from .models import ExtractRequest, ExtractResponse, ExtractOptions, Meta
from .token_estimator import estimate_tokens
from .config import settings


router = APIRouter()


def _process_pdf(pdf_bytes: bytes, options: ExtractOptions) -> ExtractResponse:
    """Gemeinsame Logik für URL und Upload Extraktion."""
    pages = extract_pdf(pdf_bytes, options)
    full_text_parts: List[str] = [page.text for page in pages]
    full_text = "\n\n".join(part for part in full_text_parts if part)

    char_count = len(full_text)
    token_estimate = estimate_tokens(full_text)

    meta = Meta(
        page_count=len(pages),
        char_count=char_count,
        token_estimate=token_estimate,
    )

    return ExtractResponse(meta=meta, full_text=full_text, pages=pages)


@router.post("/extract", response_model=ExtractResponse)
async def extract(request: ExtractRequest) -> ExtractResponse:
    """Extrahiert Text aus einer PDF-URL."""
    pdf_bytes = await fetch_pdf_from_url(str(request.source.url))
    return _process_pdf(pdf_bytes, request.options)


@router.post("/extract/upload", response_model=ExtractResponse)
async def extract_upload(
    file: UploadFile = File(..., description="PDF-Datei zum Extrahieren"),
    normalize_whitespace: bool = Form(True),
    remove_headers_footers: bool = Form(True),
    mode: str = Form("paragraphs"),
) -> ExtractResponse:
    """Extrahiert Text aus einer hochgeladenen PDF-Datei."""
    
    # Validiere Content-Type
    if file.content_type not in ["application/pdf", "application/x-pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ungültiger Dateityp: {file.content_type}. Nur PDF erlaubt.",
        )
    
    # Lese Datei
    pdf_bytes = await file.read()
    
    # Prüfe Größe
    if len(pdf_bytes) > settings.pdf_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF ist größer als erlaubte Max-Größe von {settings.pdf_max_bytes} Bytes",
        )
    
    options = ExtractOptions(
        normalize_whitespace=normalize_whitespace,
        remove_headers_footers=remove_headers_footers,
        mode=mode,
    )
    
    return _process_pdf(pdf_bytes, options)


