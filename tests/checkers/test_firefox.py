import pytest
from scripts.checkers.firefox import FirefoxVersionChecker
from .conftest import MockResponse

MOCK_FIREFOX_DESKTOP_RESPONSE = {"LATEST_FIREFOX_VERSION": "121.0"}

MOCK_FIREFOX_MOBILE_RESPONSE = {"version": "121.0", "ios_version": "121.0"}


@pytest.mark.asyncio
async def test_firefox_fetch_desktop_success(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = FirefoxVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure mock response
    mock_client.get.return_value = MockResponse(200, MOCK_FIREFOX_DESKTOP_RESPONSE)

    result = await checker.fetch_latest_version("windows")
    assert result is not None
    assert result["version"] == "121.0"
    assert result["check_method"] == "api"


@pytest.mark.asyncio
async def test_firefox_fetch_mobile_success(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = FirefoxVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure mock response
    mock_client.get.return_value = MockResponse(200, MOCK_FIREFOX_MOBILE_RESPONSE)

    result = await checker.fetch_latest_version("android")
    assert result is not None
    assert result["version"] == "121.0"
    assert result["check_method"] == "api"


@pytest.mark.asyncio
async def test_firefox_fetch_error(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = FirefoxVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure error response
    mock_client.get.return_value = MockResponse(500, None)

    result = await checker.fetch_latest_version("windows")
    assert result is None


def test_firefox_supported_platforms():
    checker = FirefoxVersionChecker()
    platforms = checker.get_supported_platforms()
    assert "windows" in platforms
    assert "macos" in platforms
    assert "ios" in platforms
    assert "android" in platforms
