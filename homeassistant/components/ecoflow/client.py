"""EcoFlow HTTP API client."""

import hashlib
import hmac
import random
import time
from typing import Any

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

    def _get_qstr(self, params: dict[str, Any]) -> str:
        """Generate query string from parameters."""
        if not params:
            return ""
        return "&".join([f"{key}={params[key]}" for key in sorted(params.keys())])

    def _get_map(self, json_obj: dict, prefix: str = "") -> dict[str, Any]:
        """Flatten JSON object for signature generation."""

        def flatten(obj: Any, pre: str = "") -> dict[str, Any]:
            result = {}
            if isinstance(obj, dict):
                for k, v in obj.items():
                    result.update(flatten(v, f"{pre}.{k}" if pre else k))
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    result.update(flatten(item, f"{pre}[{i}]"))
            else:
                result[pre] = obj
            return result

        return flatten(json_obj, prefix)

    def _hmac_sha256(self, data: str, key: str) -> str:
        """Generate HMAC-SHA256 signature."""
        hashed = hmac.new(
            key.encode("utf-8"), data.encode("utf-8"), hashlib.sha256
        ).digest()
        return hashed.hex()

    async def async_get_device_quota(self) -> dict[str, Any]:
        """Get device quota information."""
        nonce = str(random.randint(100000, 999999))
        timestamp = str(int(time.time() * 1000))

        headers = {
            "accessKey": self._access_key,
            "nonce": nonce,
            "timestamp": timestamp,
        }

        # For /quota/all endpoint, we include device SN as query parameter
        params = {"sn": self._device_sn}

        # Generate signature using the working method
        sign_str = (
            self._get_qstr(self._get_map(params)) + "&" if params else ""
        ) + self._get_qstr(headers)
        headers["sign"] = self._hmac_sha256(sign_str, self._secret_key)

        url = f"{API_BASE_URL}{API_QUOTA_ALL}"

        async with self._session.get(url, headers=headers, params=params) as response:
            if response.status != 200:
                raise EcoFlowApiError(
                    f"HTTP {response.status}: {await response.text()}"
                )

            data = await response.json()

            if data.get("code") != "0":
                raise EcoFlowApiError(
                    f"API Error {data.get('code')}: {data.get('message')}"
                )

            return data.get("data", {})

    async def async_test_connection(self) -> bool:
        """Test the connection to the EcoFlow API."""
        try:
            await self.async_get_device_quota()
        except EcoFlowApiError:
            return False
        else:
            return True
