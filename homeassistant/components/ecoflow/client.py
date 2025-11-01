"""EcoFlow HTTP API client."""

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import aiohttp

from .const import API_BASE_URL, API_QUOTA_ALL


class EcoFlowApiError(Exception):
    """Exception for EcoFlow API errors."""


class EcoFlowClient:
    """EcoFlow API client."""

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        device_sn: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the EcoFlow client."""
        self._access_key = access_key
        self._secret_key = secret_key
        self._device_sn = device_sn
        self._session = session

    def _generate_signature(self, params: dict[str, Any], timestamp: str) -> str:
        """Generate HMAC signature for API request."""
        # Sort parameters and create query string
        sorted_params = dict(sorted(params.items()))
        query_string = urlencode(sorted_params)

        # Create signature string
        signature_string = f"{query_string}&timestamp={timestamp}&accessKey={self._access_key}"

        # Generate HMAC-SHA256 signature
        return hmac.new(
            self._secret_key.encode("utf-8"),
            signature_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _check_api_response(self, data: dict[str, Any]) -> dict[str, Any]:
        """Check API response and raise error if needed."""
        if data.get("code") != "0":
            raise EcoFlowApiError(f"API error: {data.get('message', 'Unknown error')}")
        return data.get("data", {})

    async def async_get_device_quota(self) -> dict[str, Any]:
        """Get all device quota/status data."""
        timestamp = str(int(time.time() * 1000))
        params = {"sn": self._device_sn}

        # Generate signature
        signature = self._generate_signature(params, timestamp)

        # Prepare headers
        headers = {
            "accessKey": self._access_key,
            "timestamp": timestamp,
            "sign": signature,
            "Content-Type": "application/json",
        }

        url = f"{API_BASE_URL}{API_QUOTA_ALL}"

        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with self._session.get(
                url, params=params, headers=headers, timeout=timeout
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return self._check_api_response(data)

        except aiohttp.ClientError as err:
            raise EcoFlowApiError(f"Connection error: {err}") from err
        except Exception as err:
            raise EcoFlowApiError(f"Unexpected error: {err}") from err

    async def async_test_connection(self) -> bool:
        """Test the connection to the EcoFlow API."""
        try:
            await self.async_get_device_quota()
        except EcoFlowApiError:
            return False
        else:
            return True