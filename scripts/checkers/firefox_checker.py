#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.checkers.base_checker import BaseVersionChecker
import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class FirefoxVersionChecker(BaseVersionChecker):
    def __init__(self):
        super().__init__("browsers", "firefox")
        self.api_url = "https://product-details.mozilla.org/1.0/firefox_versions.json"

    async def fetch_latest_version(self) -> Optional[Dict[str, Any]]:
        """Fetch the latest Firefox version information."""
        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Firefox version from {self.api_url}")
                response = await client.get(self.api_url)
                response.raise_for_status()

                data = response.json()
                if "LATEST_FIREFOX_VERSION" not in data:
                    raise ValueError("Invalid response format from Firefox API")

                latest_version = data["LATEST_FIREFOX_VERSION"]
                current_time = datetime.utcnow().isoformat() + "Z"

                logger.info(f"Successfully fetched Firefox version: {latest_version}")
                return {"version": latest_version, "last_checked": current_time}

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Firefox version: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching Firefox version: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching Firefox version: {str(e)}",
                exc_info=True,
            )
            return None


async def main():
    checker = FirefoxVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
