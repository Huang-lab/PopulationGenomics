import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_module(relpath: str, name: str):
    """Load a module from a path inside the repo without requiring packages."""
    full = REPO_ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, full)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
