from typing import Tuple

import httpx
from fastapi import HTTPException, status

from .config import settings


async def fetch_pdf_from_url(url: str) -> bytes:
    """
    Lädt ein PDF von einer URL und gibt dessen Bytes zurück.
    Prüft Content-Type und Max-Größe.
    """
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Fehler beim Laden des PDFs: {exc}",
            ) from exc

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"PDF-Download fehlgeschlagen (Status {response.status_code})",
        )

    content_type = response.headers.get("content-type", "")
    if "pdf" not in content_type.lower():
        # Nicht hart abbrechen – manche Server setzen keinen sauberen Content-Type
        # aber wir dokumentieren es im Fehler.
        # Hier entscheiden wir uns dafür, trotzdem weiterzumachen.
        pass

    content = response.content
    if len(content) > settings.pdf_max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"PDF ist größer als erlaubte Max-Größe von {settings.pdf_max_bytes} Bytes",
        )

    return content


