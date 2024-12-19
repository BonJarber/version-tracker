import pytest
from scripts.checkers.chrome import ChromeVersionChecker
from .conftest import MockResponse

MOCK_CHROME_RESPONSE = {
    "versions": [
        {"version": "120.0.6099.129"},
        {"version": "120.0.6099.128"},
    ]
}


@pytest.mark.asyncio
async def test_chrome_fetch_success(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = ChromeVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure mock response
    mock_client.get.return_value = MockResponse(200, MOCK_CHROME_RESPONSE)

    # Test version fetch for Windows
    result = await checker.fetch_latest_version("windows")
    assert result is not None
    assert result["version"] == "120.0.6099.129"
    assert result["check_method"] == "api"


@pytest.mark.asyncio
async def test_chrome_fetch_error(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = ChromeVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure error response
    mock_client.get.return_value = MockResponse(500, None)

    result = await checker.fetch_latest_version("windows")
    assert result is None


def test_chrome_supported_platforms():
    checker = ChromeVersionChecker()
    platforms = checker.get_supported_platforms()
    assert "windows" in platforms
    assert "macos" in platforms
    assert "ios" in platforms
    assert "android" in platforms
