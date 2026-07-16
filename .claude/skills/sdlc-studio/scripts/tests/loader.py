"""The one authority for importing a script under test (US0190/CR0317).

Every test module used to open with the same ~8-line importlib incantation
(spec_from_file_location + sys.modules registration); a new module written with
a plain `import flow` fails at discovery because the scripts directory is not a
package. `load_script` is that incantation, once:

    import loader
    flow = loader.load_script("flow")

Registered in sys.modules under the bare name, so intra-script imports
(`import flow` inside deploy.py) resolve to the same module object the test
loaded - the monkeypatch-through-the-module rule (L-0057) keeps working.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent


def load_script(name: str):
    """Load `scripts/<name>.py` as module `name`, registering it in sys.modules.
    Idempotent: a module already loaded is returned as-is (never re-executed,
    so module-level state and prior monkeypatches survive)."""
    path = SCRIPTS_DIR / f"{name}.py"
    if name in sys.modules:
        cached = sys.modules[name]
        if getattr(cached, "__file__", None) == str(path):
            return cached
        # the name is held by a FOREIGN module (a stdlib/third-party collision):
        # returning it would silently hand the test the wrong code - refuse
        raise ImportError(f"sys.modules[{name!r}] is {getattr(cached, '__file__', '?')}, "
                          f"not {path} - rename the script or load it explicitly")
    if not path.is_file():
        raise FileNotFoundError(f"no script at {path} - load_script takes the bare "
                                f"module name of a file under scripts/")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod
