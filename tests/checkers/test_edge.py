import pytest
from scripts.checkers.edge import EdgeVersionChecker
from .conftest import MockResponse

MOCK_EDGE_RESPONSE = [
    {
        "Product": "Stable",
        "Releases": [
            {
                "Platform": "Windows",
                "Architecture": "x64",
                "ProductVersion": "120.0.2210.121",
            },
            {
                "Platform": "Windows",
                "Architecture": "arm64",
                "ProductVersion": "120.0.2210.121",
            },
            {
                "Platform": "MacOS",
                "Architecture": "universal",
                "ProductVersion": "120.0.2210.121",
            },
        ],
    },
    {
        "Product": "Beta",
        "Releases": [{"Platform": "Windows", "ProductVersion": "121.0.0.0"}],
    },
]


@pytest.mark.asyncio
async def test_edge_fetch_success(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = EdgeVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure mock response
    mock_client.get.return_value = MockResponse(200, MOCK_EDGE_RESPONSE)

    # Test version fetch for Windows
    result = await checker.fetch_latest_version("windows")
    assert result is not None
    assert result["version"] == "120.0.2210.121"
    assert result["check_method"] == "api"

    # Test version fetch for macOS
    result = await checker.fetch_latest_version("macos")
    assert result is not None
    assert result["version"] == "120.0.2210.121"
    assert result["check_method"] == "api"


@pytest.mark.asyncio
async def test_edge_fetch_error(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = EdgeVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure error response
    mock_client.get.return_value = MockResponse(500, None)

    result = await checker.fetch_latest_version("windows")
    assert result is None


def test_edge_supported_platforms():
    checker = EdgeVersionChecker()
    platforms = checker.get_supported_platforms()
    assert "windows" in platforms
    assert "macos" in platforms
    assert "linux" in platforms
    assert "ios" in platforms
    assert "android" in platforms
