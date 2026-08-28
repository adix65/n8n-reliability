import json
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> dict:
        with (FIXTURES_DIR / f"{name}.json").open() as f:
            return json.load(f)

    return _load
