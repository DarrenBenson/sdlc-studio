# Python Examples

Code patterns and snippets for Python.

---

## YAML Safe Loading

```python
# CORRECT - safe loading
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f) or {}

# WRONG - vulnerable to arbitrary code execution
config = yaml.load(f)  # NEVER DO THIS
config = yaml.load(f, Loader=yaml.FullLoader)  # Only for trusted sources
```

**Why:** `yaml.load()` without SafeLoader can execute arbitrary Python code via `!!python/object` tags.

---

## HTTP Requests

### Timeouts

```python
import requests

# GOOD - explicit timeouts (connect, read)
response = requests.post(url, json=data, timeout=(5.0, 120.0))

# BAD - no timeout, can hang forever
response = requests.post(url, json=data)
```

### Sessions for Multiple Requests

```python
# GOOD - connection pooling
with requests.Session() as session:
    session.headers.update({"Authorization": f"Bearer {token}"})
    session.post(url1, json=data1, timeout=(5, 120))
    session.post(url2, json=data2, timeout=(5, 120))
```

### Error Handling

```python
try:
    response = session.post(url, json=data, timeout=(5, 120))
    response.raise_for_status()
except requests.Timeout:
    logger.warning("Request timed out")
except requests.ConnectionError:
    logger.error("Connection failed")
except requests.HTTPError as e:
    logger.error("HTTP error: %s", e.response.status_code)
```

---

## Image Processing (Pillow)

```python
from PIL import Image

# CORRECT - automatic resource cleanup
with Image.open(path) as im:
    im = im.resize((width, height), resample=Image.LANCZOS)
    im.save(output_path, format="PNG", optimize=True)

# WRONG - may leak file handles
im = Image.open(path)
im.resize((width, height))
im.save(output_path)
```

### Resampling Filters

```python
Image.LANCZOS   # Best for downscaling
Image.BICUBIC   # Good for general resizing
Image.BILINEAR  # Fast, acceptable quality
```

---

## Exception Handling

### Specific Exceptions

```python
# GOOD - specific exceptions
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON: %s", e)

# BAD - hides bugs
try:
    data = json.loads(content)
except Exception:
    pass  # What went wrong? We'll never know
```

### Top-level Entry Points

```python
import sys
import traceback

def main():
    try:
        run_pipeline()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
```

---

## Type Hints

```python
from pathlib import Path
from typing import Optional

def find_item(name: str) -> Optional[tuple[Path, dict]]:
    """Find item by name or path."""
    ...

def process_file(path: Path, *, dry_run: bool = False) -> bool:
    """Process a file, return success status."""
    ...

# Collections with generic types
def process_items(items: list[str]) -> dict[str, int]:
    ...
```

---

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# In functions - use lazy formatting
logger.debug("Processing %s", filename)
logger.info("Completed %d items", count)
logger.warning("File not found: %s", path)
logger.error("Failed to connect: %s", error)

# Configuration (usually in main)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
```

---

## API Key Security

```python
import os

# CORRECT - from environment
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError("API_KEY not set")

# CORRECT - from config file
api_key = config.get("api_key")

# WRONG - hardcoded (security vulnerability)
api_key = "sk-abc123..."  # NEVER DO THIS
```

---

## File Operations with Pathlib

```python
from pathlib import Path

# Path construction
path = Path(__file__).parent / "data" / "file.json"

# Reading
content = path.read_text()
data = path.read_bytes()

# Writing
path.write_text(json.dumps(data, indent=2))

# Checking
if path.exists() and path.is_file():
    ...

# Listing
for file in path.parent.glob("*.json"):
    process(file)
```

### Context Managers for Complex Operations

```python
# When you need more control
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

# NOT recommended - easy to forget cleanup
f = open(path)
content = f.read()
f.close()  # Missed on exception
```

---

## Testing Patterns

### Pytest Fixtures

```python
import pytest

@pytest.fixture
def temp_config(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text("key: value")
    return config_path

def test_load_config(temp_config):
    config = load_config(temp_config)
    assert config["key"] == "value"
```

### Parametrised Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("", ""),
])
def test_uppercase(input, expected):
    assert uppercase(input) == expected
```

### Mocking

```python
from unittest.mock import patch, MagicMock

def test_api_call():
    with patch("requests.post") as mock_post:
        mock_post.return_value.json.return_value = {"status": "ok"}
        result = call_api("data")
        assert result["status"] == "ok"
        mock_post.assert_called_once()
```

---

## See Also

- `python-rules.md` - Standards checklist
- `script.md` - Script structure
