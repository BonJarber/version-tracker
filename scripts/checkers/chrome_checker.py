#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any

from scripts.checkers.base_checker import BaseVersionChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromeVersionChecker(BaseVersionChecker):
    def __init__(self):
        super().__init__("browsers", "chrome")
        self.api_url = "https://versionhistory.googleapis.com/v1/chrome/platforms/all/channels/stable/versions"

    async def fetch_latest_version(self) -> Optional[Dict[str, Any]]:
        """Fetch the latest Chrome version information."""
        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Chrome version from {self.api_url}")
                response = await client.get(self.api_url)
                response.raise_for_status()

                data = response.json()
                if not data or "versions" not in data or not data["versions"]:
                    raise ValueError("Invalid response format from Chrome API")

                latest_version = data["versions"][0]["version"]
                current_time = datetime.utcnow().isoformat() + "Z"

                logger.info(f"Successfully fetched Chrome version: {latest_version}")
                return {"version": latest_version, "last_checked": current_time}

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Chrome version: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching Chrome version: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching Chrome version: {str(e)}",
                exc_info=True,
            )
            return None


async def main():
    checker = ChromeVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
