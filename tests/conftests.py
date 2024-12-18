import pytest
import json
from pathlib import Path
import tempfile
import shutil
import asyncio


@pytest.fixture
def temp_data_dir(tmp_path):
    """Create a temporary data directory for tests."""
    # Create necessary subdirectories
    browser_dir = tmp_path / "browsers"
    browser_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def event_loop():
    """Create an event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Configure asyncio to use function scope for event loops
def pytest_configure(config):
    config.addinivalue_line("asyncio_mode", "strict")
    config.addinivalue_line("asyncio_fixture_loop_scope", "function")
