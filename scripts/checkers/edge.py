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


class EdgeVersionChecker(BaseVersionChecker):
    """Checker for Microsoft Edge versions."""

    def __init__(self):
        super().__init__("edge")
        self.api_url = "https://edgeupdates.microsoft.com/api/products"
        self.supported_platforms = ["windows", "macos", "linux", "ios", "android"]

    def get_initial_data(self) -> Dict[str, Any]:
        """Get initial data structure for Edge."""
        return {
            "name": "Microsoft Edge",
            "identifier": "edge",
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

    def _extract_version_from_json(
        self, data: List[Dict[str, Any]], platform: str
    ) -> Optional[str]:
        """Extract the latest stable version for a specific platform."""
        try:
            # Find the stable product
            stable_product = next(
                (product for product in data if product["Product"] == "Stable"),
                None,
            )
            if not stable_product:
                raise ValueError("No stable product found")

            # Find releases for the specified platform
            platform_releases = [
                release
                for release in stable_product["Releases"]
                if release["Platform"].lower() == platform
            ]
            if not platform_releases:
                raise ValueError(f"No releases found for platform {platform}")

            # Get the latest version (they should all be the same per platform)
            version = platform_releases[0]["ProductVersion"]
            logger.info(f"Found Edge version {version} for {platform}")
            return version

        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Edge version data for {platform}: {e}")
            return None

    async def fetch_latest_version(self, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest Edge version information for a specific platform."""
        if platform not in self.supported_platforms:
            logger.error(f"Unsupported platform: {platform}")
            return None

        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Edge version from {self.api_url}")
                response = await client.get(self.api_url)
                response.raise_for_status()
                data = response.json()

                version = self._extract_version_from_json(data, platform)
                if not version:
                    return None

                logger.info(f"Successfully fetched Edge {platform} version: {version}")
                return {
                    "version": version,
                    "check_url": self.api_url,
                    "check_method": "api",
                }

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Edge {platform} version: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching Edge {platform} version: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching Edge {platform} version: {str(e)}",
                exc_info=True,
            )
            return None

    def get_supported_platforms(self) -> List[str]:
        """Return list of supported platforms."""
        return self.supported_platforms


async def main():
    checker = EdgeVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
