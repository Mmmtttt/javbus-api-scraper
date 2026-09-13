from __future__ import annotations

import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
for path in (REPO_ROOT, REPO_ROOT / "lib"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


# The provider imports the host protocol base at runtime. Keep these tests
# repository-local so they do not require cloning or installing the host app.
protocol_base = types.ModuleType("protocol.base")
protocol_base.ProtocolProvider = object
protocol = types.ModuleType("protocol")
protocol.base = protocol_base
sys.modules.setdefault("protocol", protocol)
sys.modules.setdefault("protocol.base", protocol_base)
