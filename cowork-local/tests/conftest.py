import asyncio
from pathlib import Path

import pytest

from coworklocal.config import Settings
from coworklocal.tools import Tools


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(token="test-token", roots=[tmp_path.resolve()])


@pytest.fixture
def tools(settings: Settings) -> Tools:
    return Tools(settings)


def run(coro):
    """Run an async coroutine from a synchronous test."""
    return asyncio.run(coro)
