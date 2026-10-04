import os
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
for folder in ("services/control-api/src", "packages/domain/src"):
    sys.path.insert(0, str(ROOT / folder))
os.umask(0o077)
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
result = unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
