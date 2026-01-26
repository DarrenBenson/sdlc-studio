# Best Practices: Python

Guidelines for Python code based on library documentation and security requirements.

## External Libraries

### YAML (PyYAML)

**CRITICAL SECURITY:** Always use `yaml.safe_load()` for untrusted input.

```python
# CORRECT - safe loading
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f) or {}

# WRONG - vulnerable to arbitrary code execution
config = yaml.load(f)  # NEVER DO THIS
config = yaml.load(f, Loader=yaml.FullLoader)  # Only for trusted sources
```

**Why:** `yaml.load()` without SafeLoader can execute arbitrary Python code via `!!python/object` tags. This is a remote code execution vulnerability if the YAML comes from untrusted sources.

### requests Library

**Key practices:**

1. **Always set timeouts** - Use tuple `(connect, read)` format:
   ```python
   timeout=(5.0, 120.0)  # 5s connect, 120s read
   ```

2. **Use sessions for multiple requests** - Connection pooling and consistent headers:
   ```python
   with get_session() as session:
       session.post(url1, json=data1)
       session.post(url2, json=data2)
   ```

3. **Handle errors specifically**:
   ```python
   try:
       response = session.post(url, json=data, timeout=(5, 120))
       response.raise_for_status()
   except requests.Timeout:
       # Handle timeout specifically
   except requests.ConnectionError:
       # Handle connection issues
   except requests.HTTPError as e:
       # Handle HTTP errors (4xx, 5xx)
   ```

### Pillow (Image Processing)

**Always use context managers:**

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

**Key practices:**

1. **Use quality resampling filters**:
   ```python
   Image.LANCZOS   # Best for downscaling
   Image.BICUBIC   # Good for general resizing
   Image.BILINEAR  # Fast, acceptable quality
   ```

2. **Specify output format explicitly**:
   ```python
   im.save(path, format="PNG", optimize=True)
   im.save(path, format="JPEG", quality=90)
   ```

3. **Handle errors gracefully**:
   ```python
   try:
       with Image.open(path) as im:
           # process
   except OSError as e:
       logger.error("Cannot process image %s: %s", path, e)
   ```

## Error Handling

### Specific Exceptions

Catch the most specific exception type:

```python
# GOOD - specific exceptions
try:
    data = json.loads(content)
except json.JSONDecodeError as e:
    logger.error("Invalid JSON: %s", e)

try:
    response = session.post(url, timeout=(5, 120))
    response.raise_for_status()
except requests.Timeout:
    logger.warning("Request timed out")
except requests.HTTPError as e:
    logger.error("HTTP error: %s", e.response.status_code)

# BAD - hides bugs
try:
    data = json.loads(content)
except Exception:
    pass  # What went wrong? We'll never know
```

### When Broad Exceptions Are OK

Top-level entry points (CLI main functions) may catch `Exception` for clean exit:

```python
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

### Never Catch These Bare

```python
# NEVER do this
except:
    pass

# NEVER do this
except Exception:
    pass  # Silently swallowing errors hides bugs
```

## Type Hints

Use type hints for function signatures:

```python
from pathlib import Path
from typing import Optional

def find_item(name: str) -> Optional[tuple[Path, dict]]:
    """Find item by name or path."""
    ...

def process_file(path: Path, *, dry_run: bool = False) -> bool:
    """Process a file, return success status."""
    ...
```

## Logging

Use the logging module, not print for debugging:

```python
import logging

logger = logging.getLogger(__name__)

# In functions
logger.debug("Processing %s", filename)
logger.info("Completed %d items", count)
logger.warning("File not found: %s", path)
logger.error("Failed to connect: %s", error)
```

## API Key Security

Never hardcode API keys:

```python
# CORRECT - from environment
api_key = os.environ.get("OPENROUTER_API_KEY")
if not api_key:
    raise ValueError("OPENROUTER_API_KEY not set")

# CORRECT - from config file
api_key = config.get("api_key")

# WRONG - hardcoded (security vulnerability)
api_key = "sk-or-v1-abc123..."  # NEVER DO THIS
```

## File Operations

Use pathlib and context managers:

```python
from pathlib import Path

# GOOD
path = Path(__file__).parent / "data" / "file.json"
content = path.read_text()

with open(path, "w") as f:
    json.dump(data, f, indent=2)

# BAD
path = os.path.join(os.path.dirname(__file__), "data", "file.json")
f = open(path)
content = f.read()
f.close()  # Easy to forget, no cleanup on exception
```

## Checklist

Before completing Python code:

- [ ] YAML loading uses `safe_load()` only
- [ ] HTTP requests have explicit timeouts
- [ ] HTTP requests use sessions for multiple calls
- [ ] Image operations use context managers
- [ ] Exceptions are specific, not bare `except:`
- [ ] API keys come from environment/config
- [ ] File paths use pathlib
- [ ] Type hints on public functions
- [ ] Logging instead of print for debugging

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `yaml.load(f)` | Remote code execution | Use `yaml.safe_load(f)` |
| `requests.post(url)` | No timeout, hangs forever | Add `timeout=(5, 120)` |
| `except Exception: pass` | Hides bugs | Catch specific exceptions |
| `open(path)` without `with` | Resource leak | Use `with open()` or pathlib |
| Hardcoded API keys | Security breach | Use environment variables |
| `Image.open(path)` without `with` | File handle leak | Use context manager |
