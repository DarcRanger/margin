"""Global test isolation established before application modules are imported."""

import atexit
import os
import shutil
import tempfile

_TEST_ROOT = tempfile.mkdtemp(prefix="margin-pytest-root-")
os.environ["MARGIN_CONFIG_DIR"] = os.path.join(_TEST_ROOT, "config")
os.environ["MARGIN_WORKSPACE_DIR"] = os.path.join(_TEST_ROOT, "workspace")
atexit.register(shutil.rmtree, _TEST_ROOT, ignore_errors=True)
