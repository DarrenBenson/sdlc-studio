# OpenAPI Best Practices

Best practices for designing OpenAPI 3.1-compliant REST APIs with FastAPI.

## Specification Version

Use **OpenAPI 3.1.1** (current stable). FastAPI supports this via:

```python
from fastapi import FastAPI
app = FastAPI(openapi_version="3.1.0")
```

## Required Root Fields

Every OpenAPI document must include:

1. `openapi` - Version string (e.g., "3.1.0")
2. `info` - Object with required `title` and `version`
3. At least one of: `paths`, `components`, or `webhooks`

## API Versioning

Use URL path versioning:

```python
app.include_router(router, prefix="/api/v1")
```

- `/api/v1/resources` - Version 1
- `/api/v2/resources` - Version 2 (breaking changes)

Never remove old versions abruptly - deprecate with clear headers first.

## Resource Naming

- **Use nouns**, not verbs: `/engrams` not `/getEngrams`
- **Plural collections**: `/engrams`, `/users`, `/files`
- **Consistent hierarchy**: `/engrams/{slug}/files/{filename}`
- **Lowercase with hyphens**: `/user-guides` not `/userGuides`

## HTTP Methods

| Method | Purpose | Idempotent |
|--------|---------|------------|
| GET | Retrieve resource(s) | Yes |
| POST | Create resource | No |
| PUT | Replace resource | Yes |
| PATCH | Partial update | No |
| DELETE | Remove resource | Yes |

## Status Codes

**Success (2xx):**
- `200` - OK (GET, PUT, PATCH)
- `201` - Created (POST)
- `204` - No Content (DELETE)

**Client Error (4xx):**
- `400` - Bad Request (validation failed)
- `401` - Unauthorised (no/invalid auth)
- `403` - Forbidden (auth valid, permission denied)
- `404` - Not Found
- `409` - Conflict (duplicate, state conflict)
- `422` - Unprocessable Entity (semantic error)

**Server Error (5xx):**
- `500` - Internal Server Error
- `503` - Service Unavailable

## Error Responses

Standardise error format:

```python
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    field: str | None = None

# In FastAPI
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

## Pagination

For list endpoints:

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    limit: int
    pages: int

@router.get("/engrams")
async def list_engrams(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("name"),
    order: str = Query("asc", pattern="^(asc|desc)$")
) -> PaginatedResponse[EngramSummary]:
    ...
```

## Query Parameters

- **Filtering**: `?category=fictional&status=active`
- **Sorting**: `?sort_by=name&order=desc`
- **Pagination**: `?page=1&limit=20`
- **Search**: `?q=search+term`

## Schema Reuse

Use components and `$ref` to avoid repetition:

```python
# Define reusable models in models.py
class EngramBase(BaseModel):
    name: str
    role: str

class EngramCreate(EngramBase):
    slug: str
    category: str

class EngramResponse(EngramBase):
    slug: str
    category: str
    created_at: datetime
```

## Security Schemes

Document authentication in FastAPI:

```python
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
```

## Documentation

Enhance OpenAPI output:

```python
app = FastAPI(
    title="Engram Library API",
    description="API for managing engram identities",
    version="1.0.0",
    contact={"name": "Support", "email": "support@example.com"},
    license_info={"name": "MIT"},
    servers=[
        {"url": "https://api.example.com", "description": "Production"},
        {"url": "http://localhost:8001", "description": "Development"}
    ]
)
```

Add descriptions to endpoints:

```python
@router.get(
    "/engrams/{slug}",
    summary="Get engram by slug",
    description="Retrieves full engram details including psychometrics and user manual.",
    response_description="The engram details"
)
```

## File Operations

For file uploads/downloads:

```python
from fastapi import UploadFile, File
from fastapi.responses import FileResponse

@router.post("/engrams/{slug}/files")
async def upload_file(
    slug: str,
    file: UploadFile = File(...),
    api_key: str = Security(verify_api_key)
):
    ...

@router.get("/engrams/{slug}/files/{filename}")
async def get_file(slug: str, filename: str):
    return FileResponse(path, filename=filename)
```

## Design-First Workflow

1. Define API contract in OpenAPI/Pydantic models first
2. Implement endpoints to match the contract
3. Use CI to validate spec matches implementation
4. Generate client SDKs from OpenAPI spec

## Validation Tools

- **Spectral** - OpenAPI linting
- **Redocly** - Spec validation and documentation
- **FastAPI /docs** - Auto-generated Swagger UI
- **FastAPI /redoc** - Auto-generated ReDoc

## Sources

- [OpenAPI Specification 3.1.1](https://swagger.io/specification/)
- [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
