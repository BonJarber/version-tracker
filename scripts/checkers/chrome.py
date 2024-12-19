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


class ChromeVersionChecker(BaseVersionChecker):
    """Checker for Chrome versions."""

    def __init__(self):
        super().__init__("chrome")
        self.base_url = "https://versionhistory.googleapis.com/v1/chrome/platforms"
        self.platform_mapping = {
            "windows": "win",
            "macos": "mac",
            "ios": "ios",
            "android": "android",
        }

    def get_initial_data(self) -> Dict[str, Any]:
        """Get initial data structure for Chrome."""
        return {
            "name": "Google Chrome",
            "identifier": "chrome",
            "type": "browser",
            "platforms": list(self.platform_mapping.keys()),
            "versions": {
                "platforms": {
                    platform: {
                        "version": "0.0.0",  # Placeholder version
                        "check_url": self._get_platform_url(platform),
                        "check_method": "api",
                    }
                    for platform in self.platform_mapping.keys()
                }
            },
            "metadata": {"last_checked": datetime.utcnow().isoformat() + "Z"},
        }

    def _get_platform_url(self, platform: str) -> str:
        """Get the version check URL for a specific platform."""
        return f"{self.base_url}/{self.platform_mapping[platform]}/channels/stable/versions"

    async def fetch_latest_version(self, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest Chrome version information for a specific platform."""
        if platform not in self.platform_mapping:
            logger.error(f"Unsupported platform: {platform}")
            return None

        try:
            url = self._get_platform_url(platform)
            async with await self.get_client() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

                if not data or "versions" not in data or not data["versions"]:
                    raise ValueError(
                        f"Invalid response format from Chrome API for {platform}"
                    )

                version = data["versions"][0]["version"]

                logger.info(
                    f"Successfully fetched Chrome {platform} version: {version}"
                )
                return {"version": version, "check_url": url, "check_method": "api"}

        except httpx.TimeoutException as e:
            logger.error(f"Timeout while fetching Chrome {platform} version: {e}")
            return None
        except httpx.HTTPError as e:
            logger.error(f"HTTP error while fetching Chrome {platform} version: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error while fetching Chrome {platform} version: {str(e)}",
                exc_info=True,
            )
            return None

    def get_supported_platforms(self) -> List[str]:
        """Return list of supported platforms."""
        return list(self.platform_mapping.keys())


async def main():
    checker = ChromeVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
