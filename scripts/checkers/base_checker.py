import httpx
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class BaseVersionChecker:
    """Base class for version checkers with platform support."""

    def __init__(self, product_name: str):
        """Initialize checker with product name.

        Args:
            product_name: Name of the product (e.g., 'chrome', 'firefox')
        """
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_file = self.base_dir / "data" / f"{product_name}.json"
        self.schema_file = self.base_dir / "schemas" / "product.schema.json"
        self.schema = self.load_schema()

    def get_initial_data(self) -> Dict[str, Any]:
        """Get initial data structure. Should be overridden by subclasses."""
        raise NotImplementedError("Subclasses must implement get_initial_data")

    def ensure_data_file(self):
        """Create data file with initial structure if it doesn't exist."""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            initial_data = self.get_initial_data()
            try:
                validate(instance=initial_data, schema=self.schema)
                with open(self.data_file, "w") as f:
                    json.dump(initial_data, f, indent=2)
                    f.write("\n")
            except Exception as e:
                logger.error(f"Failed to create initial data file: {e}")
                raise

    def read_current_data(self) -> Dict[str, Any]:
        """Read and validate the current data file."""

        self.ensure_data_file()

        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)
                validate(instance=data, schema=self.schema)
                return data
        except Exception as e:
            logger.error(f"Error reading/validating data file: {e}")
            raise

    def load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation."""
        try:
            with open(self.schema_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Schema file not found at {self.schema_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file: {e}")
            raise

    async def fetch_latest_version(self, platform: str) -> Optional[Dict[str, Any]]:
        """Fetch the latest version information for a specific platform.

        Args:
            platform: Target platform (e.g., 'windows', 'macos')

        Returns:
            Dict containing version info or None if fetch fails
        """
        raise NotImplementedError("Subclasses must implement fetch_latest_version")

    def get_supported_platforms(self) -> List[str]:
        """Get list of platforms supported by this product."""
        data = self.read_current_data()
        return data.get("platforms", [])

    def write_updated_data(self, data: Dict[str, Any]):
        """Validate and write updated data back to the data file."""
        try:
            validate(instance=data, schema=self.schema)

            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")

        except ValidationError as e:
            logger.error(f"Updated data fails schema validation: {e}")
            raise

    async def get_client(self) -> httpx.AsyncClient:
        """Get a configured HTTP client."""
        return httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=5.0),
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; version-checker/1.0)",
                "Accept": "application/json",
            },
            follow_redirects=True,
        )

    async def update(self, platforms: Optional[List[str]] = None) -> bool:
        """Update version information for specified platforms."""
        try:
            current_data = self.read_current_data()
            target_platforms = platforms or self.get_supported_platforms()
            success = True

            for platform in target_platforms:
                try:
                    latest_info = await self.fetch_latest_version(platform)
                    if not latest_info:
                        logger.error(f"Failed to fetch latest version for {platform}")
                        success = False
                        continue

                    if "platforms" not in current_data["versions"]:
                        current_data["versions"]["platforms"] = {}

                    current_data["versions"]["platforms"][platform] = {
                        "version": latest_info["version"],
                        "check_url": latest_info["check_url"],
                        "check_method": latest_info["check_method"],
                    }

                except Exception as e:
                    logger.error(f"Error updating {platform} version: {e}")
                    success = False

            current_data["metadata"]["last_checked"] = (
                datetime.utcnow().isoformat() + "Z"
            )

            self.write_updated_data(current_data)
            return success

        except Exception as e:
            logger.error(f"Error in update process: {e}")
            return False
