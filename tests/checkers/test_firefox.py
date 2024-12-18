import pytest
import json
from pathlib import Path
import httpx
from datetime import datetime
from unittest.mock import Mock, patch
from scripts.checkers.firefox_checker import FirefoxVersionChecker


@pytest.fixture
def firefox_data(tmp_path):
    """Create a temporary Firefox data file."""
    data = {
        "name": "Mozilla Firefox",
        "identifier": "firefox",
        "type": "browser",
        "versions": {"stable": {"version": "100.0.0"}},
        "metadata": {
            "last_checked": "2024-12-17T00:00:00Z",
            "check_method": "api",
            "check_url": "https://product-details.mozilla.org/1.0/firefox_versions.json",
        },
    }

    browsers_dir = tmp_path / "browsers"
    browsers_dir.mkdir()
    data_file = browsers_dir / "firefox.json"

    with open(data_file, "w") as f:
        json.dump(data, f)
    return data_file


@pytest.fixture
def mock_firefox_response():
    """Mock Firefox API response."""
    return {
        "FIREFOX_NIGHTLY": "135.0a1",
        "FIREFOX_DEVEDITION": "134.0b10",
        "FIREFOX_ESR": "115.6.0esr",
        "LATEST_FIREFOX_VERSION": "133.0.3",
        "LATEST_FIREFOX_DEVEL_VERSION": "134.0b10",
    }


class TestFirefoxVersionChecker:
    @pytest.mark.asyncio
    async def test_fetch_latest_version_success(self, mock_firefox_response):
        """Test successful version fetch."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_firefox_response)
            )

            checker = FirefoxVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is not None
            assert result["version"] == "133.0.3"
            assert "last_checked" in result

    @pytest.mark.asyncio
    async def test_fetch_latest_version_timeout(self):
        """Test handling of timeout error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")

            checker = FirefoxVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_latest_version_http_error(self):
        """Test handling of HTTP error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.HTTPError("HTTP Error")

            checker = FirefoxVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_latest_version_missing_key(self, mock_firefox_response):
        """Test handling of missing version key in response."""
        mock_firefox_response.pop("LATEST_FIREFOX_VERSION")

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_firefox_response)
            )

            checker = FirefoxVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    def test_read_current_data(self, firefox_data):
        """Test reading current data file."""
        checker = FirefoxVersionChecker()
        checker.data_file = firefox_data

        data = checker.read_current_data()
        assert data["name"] == "Mozilla Firefox"
        assert data["versions"]["stable"]["version"] == "100.0.0"

    @pytest.mark.asyncio
    async def test_update_success(self, firefox_data, mock_firefox_response):
        """Test successful update process."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_firefox_response)
            )

            checker = FirefoxVersionChecker()
            checker.data_file = firefox_data

            success = await checker.update()
            assert success is True

            # Verify file was updated
            with open(firefox_data) as f:
                updated_data = json.load(f)
                assert updated_data["versions"]["stable"]["version"] == "133.0.3"
                assert "last_checked" in updated_data["metadata"]
