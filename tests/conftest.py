import pytest
import sys
from pathlib import Path


# Ensure the repository's src/ is importable in tests
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"
