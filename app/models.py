from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl, Field


class ExtractMode(str, Enum):
    PARAGRAPHS = "paragraphs"
    PAGES = "pages"
    FULL_TEXT = "full_text"


class Source(BaseModel):
    url: HttpUrl = Field(..., description="Öffentlich erreichbare URL zum PDF")


class ExtractOptions(BaseModel):
    normalize_whitespace: bool = True
    remove_headers_footers: bool = True
    mode: ExtractMode = ExtractMode.PARAGRAPHS


class ExtractRequest(BaseModel):
    source: Source
    options: ExtractOptions = ExtractOptions()


class PageParagraph(BaseModel):
    index: int
    text: str


class Page(BaseModel):
    page_number: int
    text: str
    paragraphs: List[PageParagraph]


class Meta(BaseModel):
    page_count: int
    char_count: int
    token_estimate: int


class ExtractResponse(BaseModel):
    meta: Meta
    full_text: str
    pages: List[Page]



