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


class SafariVersionChecker(BaseVersionChecker):
    def __init__(self):
        super().__init__("browsers", "safari")
        self.api_url = "https://developer.apple.com/tutorials/data/documentation/safari-release-notes.json"

    async def fetch_latest_version(self) -> Optional[Dict[str, Any]]:
        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Safari version from {self.api_url}")
                response = await client.get(self.api_url)

                response.raise_for_status()
                data = response.json()

                # Parse the data to get the latest version
                latest_version = data["topicSections"][0]["identifiers"][0]
                latest_version = latest_version.split("/")[-1]
                latest_version = latest_version.replace("safari-", "")
                latest_version = latest_version.replace("-release-notes", "")
                latest_version = latest_version.replace("_", ".")
                current_time = datetime.utcnow().isoformat() + "Z"

                logger.info(f"Successfully fetched Safari version: {latest_version}")
                return {"version": latest_version, "last_checked": current_time}

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Safari version: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching Safari version: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching Safari version: {str(e)}",
                exc_info=True,
            )
            return None


async def main():
    checker = SafariVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
