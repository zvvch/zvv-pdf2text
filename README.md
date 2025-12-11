# PDF Extract Service

A high-performance, self-hosted PDF-to-text extraction API built with FastAPI and PyMuPDF.

**Live:** https://pdf2text.rapold.io

## Features

- **🔗 URL Extraction**: Fetch PDFs directly from any public URL
- **📁 File Upload**: Upload local PDFs via drag & drop
- **🧹 Smart Line Joining**: Automatically fixes broken PDF line breaks
- **🗑️ Header/Footer Removal**: Detects and removes repeated page elements
- **📊 Token Estimation**: GPT-compatible token count for cost planning
- **💾 TXT Download**: Export extracted text as .txt file
- **🎨 Modern Web UI**: Dark theme, responsive design

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 https://pdf2text.rapold.io                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  Frontend   │───▶│   FastAPI   │───▶│   PyMuPDF   │    │
│   │  (HTML/JS)  │◀───│  (uvicorn)  │◀───│ Extraction  │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│                             │                               │
│                             ▼                               │
│                      ┌─────────────┐                        │
│                      │    httpx    │                        │
│                      │ PDF Download│                        │
│                      └─────────────┘                        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  Cloudflare Tunnel: mra_pve1_net → LXC 104 (192.168.1.86)  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Local Development

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Deployment

```bash
docker build -t pdf-extract-service:latest .
docker run -d --name pdf-extract-service -p 8000:8000 --restart unless-stopped pdf-extract-service:latest
```

## API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI (Frontend) |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |
| `POST` | `/extract` | Extract from URL |
| `POST` | `/extract/upload` | Extract from uploaded file |

### POST /extract (URL)

```bash
curl -X POST https://pdf2text.rapold.io/extract \
  -H "Content-Type: application/json" \
  -d '{
    "source": {"url": "https://example.com/doc.pdf"},
    "options": {
      "normalize_whitespace": true,
      "remove_headers_footers": true,
      "mode": "paragraphs"
    }
  }'
```

### POST /extract/upload (File)

```bash
curl -X POST https://pdf2text.rapold.io/extract/upload \
  -F "file=@document.pdf" \
  -F "normalize_whitespace=true" \
  -F "remove_headers_footers=true" \
  -F "mode=paragraphs"
```

### Response Format

```json
{
  "meta": {
    "page_count": 14,
    "char_count": 46014,
    "token_estimate": 11504
  },
  "full_text": "Complete extracted text...",
  "pages": [
    {
      "page_number": 1,
      "text": "Page 1 text...",
      "paragraphs": [
        {"index": 0, "text": "First paragraph..."}
      ]
    }
  ]
}
```

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `normalize_whitespace` | bool | `true` | Join broken lines, clean whitespace |
| `remove_headers_footers` | bool | `true` | Remove repeated header/footer text |
| `mode` | string | `"paragraphs"` | `"paragraphs"` or `"full"` |

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `PDF_MAX_MB` | `50` | Maximum PDF file size in MB |
| `HTTP_TIMEOUT_SECONDS` | `30` | Timeout for URL downloads |

## Project Structure

```
pdf-extract-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + routes
│   ├── api.py               # /extract + /extract/upload
│   ├── models.py            # Pydantic models
│   ├── extractor.py         # PyMuPDF + line joining
│   ├── http_client.py       # Async PDF download
│   ├── header_footer.py     # Header/footer detection
│   ├── token_estimator.py   # GPT token estimation
│   ├── config.py            # Settings
│   └── static/
│       └── index.html       # Frontend UI
├── requirements.txt
├── Dockerfile
└── README.md
```

## Deployment

### Production (Proxmox LXC + Cloudflare Tunnel)

**Live URLs:**
- https://pdf2text.rapold.io – PDF Extract Service
- https://pve1.rapold.io – Proxmox Web UI

**Infrastructure:**
- LXC Container: CTID 104 (`pdf-extract`)
- IP: 192.168.1.86
- Cloudflare Tunnel: `mra_pve1_net`

```bash
# On Proxmox host (PVE-1)
ssh pve1

# Check tunnel status
cloudflared tunnel list

# Check container
pct exec 104 -- docker ps

# View logs
pct exec 104 -- docker logs pdf-extract-service
```

## Error Codes

| HTTP Status | Meaning |
|-------------|---------|
| `200` | Success |
| `400` | Invalid request / bad file type |
| `413` | PDF exceeds size limit |
| `502` | Failed to download PDF from URL |
| `500` | Internal extraction error |

## Tech Stack

- **FastAPI** – Async Python web framework
- **PyMuPDF** – PDF text extraction
- **httpx** – Async HTTP client
- **Pydantic** – Data validation
- **Docker** – Containerization
- **Cloudflare Tunnel** – Zero-trust access

---

**Maintainer**: RadioX Team  
**Version**: 0.2.0
