"""Backend package bootstrap.

Ensures legacy absolute imports such as ``from services import ...`` continue to
work whether the app is started from the repository root (``backend.app``) or
from inside ``backend`` (``app``).
"""

from __future__ import annotations

import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
_backend_dir_str = str(_BACKEND_DIR)

# Keep backend directory importable as a top-level search root for historical
# absolute imports used across the codebase (services.*, routes.*, database.*).
if _backend_dir_str not in sys.path:
    sys.path.insert(0, _backend_dir_str)
