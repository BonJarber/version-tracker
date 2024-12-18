import pytest
import json
from pathlib import Path
import httpx
from datetime import datetime
from unittest.mock import Mock, patch
from scripts.checkers.chrome_checker import ChromeVersionChecker


@pytest.fixture
def chrome_data(tmp_path):
    """Create a temporary Chrome data file."""
    data = {
        "name": "Google Chrome",
        "identifier": "chrome",
        "type": "browser",
        "versions": {"stable": {"version": "100.0.0.0"}},
        "metadata": {
            "last_checked": "2024-12-17T00:00:00Z",
            "check_method": "api",
            "check_url": "https://versionhistory.googleapis.com/v1/chrome/platforms/all/channels/stable/versions",
        },
    }

    browsers_dir = tmp_path / "browsers"
    browsers_dir.mkdir()
    data_file = browsers_dir / "chrome.json"

    with open(data_file, "w") as f:
        json.dump(data, f)
    return data_file


@pytest.fixture
def mock_chrome_response():
    """Mock Chrome API response."""
    return {"versions": [{"version": "120.0.0.0", "name": "120.0.0.0"}]}


class TestChromeVersionChecker:
    @pytest.mark.asyncio
    async def test_fetch_latest_version_success(self, mock_chrome_response):
        """Test successful version fetch."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_chrome_response)
            )

            checker = ChromeVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is not None
            assert result["version"] == "120.0.0.0"
            assert "last_checked" in result

    @pytest.mark.asyncio
    async def test_fetch_latest_version_timeout(self):
        """Test handling of timeout error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")

            checker = ChromeVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_latest_version_http_error(self):
        """Test handling of HTTP error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.HTTPError("HTTP Error")

            checker = ChromeVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    def test_read_current_data(self, chrome_data):
        """Test reading current data file."""
        checker = ChromeVersionChecker()
        checker.data_file = chrome_data

        data = checker.read_current_data()
        assert data["name"] == "Google Chrome"
        assert data["versions"]["stable"]["version"] == "100.0.0.0"

    @pytest.mark.asyncio
    async def test_update_success(self, chrome_data, mock_chrome_response):
        """Test successful update process."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_chrome_response)
            )

            checker = ChromeVersionChecker()
            checker.data_file = chrome_data

            success = await checker.update()
            assert success is True

            # Verify file was updated
            with open(chrome_data) as f:
                updated_data = json.load(f)
                assert updated_data["versions"]["stable"]["version"] == "120.0.0.0"
