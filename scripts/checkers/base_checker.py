import httpx
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)


class BaseVersionChecker:
    def __init__(self, product_type: str, product_name: str):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_file = self.base_dir / "data" / product_type / f"{product_name}.json"
        self.schema_file = self.base_dir / "schemas" / "product.schema.json"
        self.schema = self.load_schema()

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

    async def fetch_latest_version(self) -> Optional[Dict[str, Any]]:
        """Fetch the latest version information. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement fetch_latest_version")

    def read_current_data(self) -> Dict[str, Any]:
        """Read and validate the current data file."""
        try:
            with open(self.data_file, "r") as f:
                data = json.load(f)

            try:
                validate(instance=data, schema=self.schema)
                return data
            except ValidationError as e:
                logger.error(f"Current data file fails schema validation: {e}")
                raise

        except FileNotFoundError:
            logger.error(f"Data file not found at {self.data_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data file: {e}")
            raise

    def write_updated_data(self, data: Dict[str, Any]):
        """Validate and write updated data back to the data file."""
        try:
            validate(instance=data, schema=self.schema)

            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")

            logger.info("Successfully validated and wrote updated data")

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

    async def update(self) -> bool:
        """Update version information using the generic workflow."""
        try:
            current_data = self.read_current_data()
            latest_info = await self.fetch_latest_version()

            if not latest_info:
                logger.error("Failed to fetch latest version")
                return False

            # Update the version information
            current_data["versions"]["stable"]["version"] = latest_info["version"]
            current_data["metadata"]["last_checked"] = latest_info["last_checked"]

            self.write_updated_data(current_data)
            logger.info(f"Successfully updated to version {latest_info['version']}")
            return True

        except Exception as e:
            logger.error(f"Error updating version: {e}")
            return False
