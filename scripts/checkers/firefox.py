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


class FirefoxVersionChecker(BaseVersionChecker):
    def __init__(self):
        super().__init__("firefox")
        self.desktop_url = (
            "https://product-details.mozilla.org/1.0/firefox_versions.json"
        )
        self.mobile_url = "https://product-details.mozilla.org/1.0/mobile_versions.json"
        self.platform_mapping = {
            "windows": "desktop",
            "macos": "desktop",
            "ios": "mobile",
            "android": "mobile",
        }

    def get_initial_data(self) -> Dict[str, Any]:
        """Get initial data structure for Firefox."""
        return {
            "name": "Mozilla Firefox",
            "identifier": "firefox",
            "type": "browser",
            "platforms": list(self.platform_mapping.keys()),
            "versions": {
                "platforms": {
                    platform: {
                        "version": "0.0.0",
                        "check_url": (
                            self.desktop_url
                            if self.platform_mapping[platform] == "desktop"
                            else self.mobile_url
                        ),
                        "check_method": "api",
                    }
                    for platform in self.platform_mapping.keys()
                }
            },
            "metadata": {"last_checked": datetime.utcnow().isoformat() + "Z"},
        }

    async def _fetch_desktop_version(self) -> Optional[str]:
        """Fetch the latest Firefox desktop version."""
        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Firefox desktop version from {self.desktop_url}")
                response = await client.get(self.desktop_url)
                response.raise_for_status()
                data = response.json()

                if "LATEST_FIREFOX_VERSION" not in data:
                    raise ValueError("Invalid response format from Firefox desktop API")

                version = data["LATEST_FIREFOX_VERSION"]
                logger.info(f"Successfully fetched Firefox desktop version: {version}")
                return version

        except Exception as e:
            logger.error(f"Error fetching Firefox desktop version: {e}")
            return None

    async def _fetch_mobile_versions(self) -> Optional[Dict[str, str]]:
        """Fetch the latest Firefox mobile versions."""
        try:
            async with await self.get_client() as client:
                logger.info(f"Fetching Firefox mobile versions from {self.mobile_url}")
                response = await client.get(self.mobile_url)
                response.raise_for_status()
                data = response.json()

                if "version" not in data:
                    raise ValueError("Invalid response format from Firefox mobile API")

                # Use iOS-specific version if available, otherwise use common version
                ios_version = data.get("ios_version") or data["version"]
                android_version = data["version"]

                logger.info(
                    f"Successfully fetched Firefox mobile versions - Android: {android_version}, iOS: {ios_version}"
                )
                return {"ios": ios_version, "android": android_version}

        except Exception as e:
            logger.error(f"Error fetching Firefox mobile versions: {e}")
            return None

    async def fetch_latest_version(self, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest Firefox version information for a specific platform."""
        if platform not in self.platform_mapping:
            logger.error(f"Unsupported platform: {platform}")
            return None

        try:
            platform_type = self.platform_mapping[platform]

            if platform_type == "desktop":
                version = await self._fetch_desktop_version()
                if not version:
                    return None
                return {
                    "version": version,
                    "check_url": self.desktop_url,
                    "check_method": "api",
                }
            else:  # mobile
                versions = await self._fetch_mobile_versions()
                if not versions:
                    return None
                return {
                    "version": versions[
                        platform
                    ],  # platform will be either "ios" or "android"
                    "check_url": self.mobile_url,
                    "check_method": "api",
                }

        except Exception as e:
            logger.error(f"Error fetching Firefox {platform} version: {e}")
            return None

    def get_supported_platforms(self) -> List[str]:
        """Return list of supported platforms."""
        return list(self.platform_mapping.keys())


async def main():
    checker = FirefoxVersionChecker()
    success = await checker.update()
    exit(0 if success else 1)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
