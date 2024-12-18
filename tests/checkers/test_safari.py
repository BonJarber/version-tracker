import pytest
import json
from pathlib import Path
import httpx
from datetime import datetime
from unittest.mock import Mock, patch
from scripts.checkers.safari_checker import SafariVersionChecker


@pytest.fixture
def safari_data(tmp_path):
    """Create a temporary Safari data file."""
    data = {
        "name": "Apple Safari",
        "identifier": "safari",
        "type": "browser",
        "versions": {"stable": {"version": "18.0"}},
        "metadata": {
            "last_checked": "2024-12-17T00:00:00Z",
            "check_method": "api",
            "check_url": "https://developer.apple.com/tutorials/data/documentation/safari-release-notes.json",
        },
    }

    browsers_dir = tmp_path / "browsers"
    browsers_dir.mkdir()
    data_file = browsers_dir / "safari.json"

    with open(data_file, "w") as f:
        json.dump(data, f)
    return data_file


@pytest.fixture
def mock_safari_response():
    """Mock Safari API response."""
    return {
        "topicSections": [
            {
                "identifiers": [
                    "doc://com.apple.Safari-Release-Notes/documentation/Safari-Release-Notes/safari-18_0-release-notes"
                ]
            }
        ]
    }


class TestSafariVersionChecker:
    @pytest.mark.asyncio
    async def test_fetch_latest_version_success(self, mock_safari_response):
        """Test successful version fetch."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_safari_response)
            )

            checker = SafariVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is not None
            assert result["version"] == "18.0"
            assert "last_checked" in result

    @pytest.mark.asyncio
    async def test_fetch_latest_version_timeout(self):
        """Test handling of timeout error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")

            checker = SafariVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_latest_version_http_error(self):
        """Test handling of HTTP error."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.side_effect = httpx.HTTPError("HTTP Error")

            checker = SafariVersionChecker()
            result = await checker.fetch_latest_version()

            assert result is None

    def test_read_current_data(self, safari_data):
        """Test reading current data file."""
        checker = SafariVersionChecker()
        checker.data_file = safari_data

        data = checker.read_current_data()
        assert data["name"] == "Apple Safari"
        assert data["versions"]["stable"]["version"] == "18.0"

    @pytest.mark.asyncio
    async def test_update_success(self, safari_data, mock_safari_response):
        """Test successful update process."""
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_get.return_value = Mock(
                raise_for_status=Mock(), json=Mock(return_value=mock_safari_response)
            )

            checker = SafariVersionChecker()
            checker.data_file = safari_data

            success = await checker.update()
            assert success is True

            # Verify file was updated
            with open(safari_data) as f:
                updated_data = json.load(f)
                assert updated_data["versions"]["stable"]["version"] == "18.0"
