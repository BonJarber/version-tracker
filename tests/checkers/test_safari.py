import pytest
from scripts.checkers.safari import SafariVersionChecker
from .conftest import MockResponse

MOCK_SAFARI_RESPONSE = {
    "interfaceLanguages": {
        "swift": [
            {
                "children": [
                    {"title": "Version 18", "type": "groupMarker"},
                    {
                        "path": "/documentation/safari-release-notes/safari-18_3-release-notes",
                        "title": "Safari 18.3 Beta Release Notes",
                        "type": "article",
                    },
                    {
                        "path": "/documentation/safari-release-notes/safari-18_2-release-notes",
                        "title": "Safari 18.2 Release Notes",
                        "type": "article",
                    },
                ]
            }
        ]
    }
}


@pytest.mark.asyncio
async def test_safari_fetch_success(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = SafariVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure mock response
    mock_client.get.return_value = MockResponse(200, MOCK_SAFARI_RESPONSE)

    # Should skip beta and return 18.2
    result = await checker.fetch_latest_version("macos")
    assert result is not None
    assert result["version"] == "18.2"
    assert result["check_method"] == "api"


@pytest.mark.asyncio
async def test_safari_fetch_error(mock_httpx_client, mocker):
    mock_client, mock_context = mock_httpx_client
    checker = SafariVersionChecker()
    mocker.patch.object(checker, "get_client", return_value=mock_context)

    # Configure error response
    mock_client.get.return_value = MockResponse(500, None)

    result = await checker.fetch_latest_version("macos")
    assert result is None


def test_safari_supported_platforms():
    checker = SafariVersionChecker()
    platforms = checker.get_supported_platforms()
    assert "macos" in platforms
    assert "ios" in platforms
    assert "windows" not in platforms
