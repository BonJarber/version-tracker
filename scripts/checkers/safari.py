#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

import httpx
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from scripts.checkers.base_checker import BaseVersionChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SafariVersionChecker(BaseVersionChecker):
    """Checker for Safari versions."""

    def __init__(self):
        super().__init__("safari")
        self.api_url = (
            "https://developer.apple.com/tutorials/data/index/safari-release-notes"
        )
        # Safari versions are universal across Apple platforms
        self.supported_platforms = ["macos", "ios"]

    def get_initial_data(self) -> Dict[str, Any]:
        """Get initial data structure for Safari."""
        return {
            "name": "Apple Safari",
            "identifier": "safari",
            "type": "browser",
            "platforms": self.supported_platforms,
            "versions": {
                "platforms": {
                    platform: {
                        "version": "0.0.0",  # Placeholder version
                        "check_url": self.api_url,
                        "check_method": "api",
                    }
                    for platform in self.supported_platforms
                }
            },
            "metadata": {"last_checked": datetime.utcnow().isoformat() + "Z"},
        }

    def _extract_version_from_json(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract the latest version number from the Safari release notes JSON."""
        try:
            # Get all child entries
            children = data["interfaceLanguages"]["swift"][0]["children"]

            # Find first non-groupMarker entry
            for child in children:
                if child["type"] == "groupMarker" or "Beta" in child.get("title", ""):
                    continue

                # Extract version from path like "/documentation/safari-release-notes/safari-18_2-release-notes"
                path = child.get("path", "")
                if not path:
                    continue

                path_parts = path.split("/")[-1].split("-")
                version = path_parts[1].replace("_", ".")
                return version

            raise ValueError("No valid version entry found in release notes")

        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Safari version data: {e}")
            return None

    async def fetch_latest_version(self, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest Safari version information."""
        if platform not in self.supported_platforms:
            logger.error(f"Unsupported platform: {platform}")
            return None

        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Safari version from {self.api_url}")
                response = await client.get(self.api_url)
                response.raise_for_status()
                data = response.json()

                version = self._extract_version_from_json(data)
                if not version:
                    return None

                logger.info(f"Successfully fetched Safari version: {version}")
                return {
                    "version": version,
                    "check_url": self.api_url,
                    "check_method": "api",
                }

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

    def get_supported_platforms(self) -> List[str]:
        """Return list of supported platforms."""
        return self.supported_platforms


async def main():
    checker = SafariVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
