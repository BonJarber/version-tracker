import pytest
import httpx
from typing import Dict, Any, Optional


class MockResponse:
    def __init__(self, status_code: int, json_data: Optional[Dict[str, Any]] = None):
        self.status_code = status_code
        self._json_data = json_data

    def json(self) -> Dict[str, Any]:
        if self._json_data is None:
            raise httpx.HTTPError("No JSON data")
        return self._json_data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "Mock error",
                request=httpx.Request("GET", "http://test.com"),
                response=self,
            )


@pytest.fixture
def mock_httpx_client(mocker):
    """Mock httpx client that can be configured per test."""
    mock_client = mocker.AsyncMock(spec=httpx.AsyncClient)
    mock_context = mocker.AsyncMock()
    mock_context.__aenter__.return_value = mock_client
    mock_context.__aexit__.return_value = None
    return mock_client, mock_context
