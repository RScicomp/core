#!/usr/bin/env python3
"""Test script to verify EcoFlow API connection."""

import asyncio
import aiohttp
import sys
import os
import hashlib
import hmac
import time
from urllib.parse import urlencode

# Add the project root to Python path
sys.path.insert(0, "/workspaces/core")

from homeassistant.components.ecoflow.client import EcoFlowClient


async def test_ecoflow_connection():
    """Test EcoFlow API connection with your credentials."""

    # Your actual credentials
    ACCESS_KEY = os.getenv("ECOFLOW_ACCESS_KEY", "")
    SECRET_KEY = os.getenv("ECOFLOW_SECRET_KEY", "")
    DEVICE_SN = os.getenv("ECOFLOW_DEVICE_SN", "")

    print("🔍 Testing EcoFlow API connection...")
    print(f"📝 Access Key: {ACCESS_KEY[:8]}...{ACCESS_KEY[-4:]}")
    print(f"📝 Device SN: {DEVICE_SN}")
    print()

    async with aiohttp.ClientSession() as session:
        client = EcoFlowClient(ACCESS_KEY, SECRET_KEY, DEVICE_SN, session)

        try:
            print("📡 Attempting to connect to EcoFlow API...")
            data = await client.async_get_device_quota()

            print("✅ Connection successful!")
            print(f"📊 Received data with {len(data)} keys")

            # Show some sample data structure
            if data:
                print("\n📋 Sample data keys:")
                for i, key in enumerate(list(data.keys())[:10]):
                    print(f"  {i + 1}. {key}")
                if len(data) > 10:
                    print(f"  ... and {len(data) - 10} more keys")

            return True

        except Exception as ex:
            print(f"❌ Connection failed: {ex}")
            print(f"🔍 Exception type: {type(ex).__name__}")

            # Try to get more details about the error
            if hasattr(ex, "status"):
                print(f"📊 HTTP Status: {ex.status}")
            if hasattr(ex, "message"):
                print(f"📝 Error message: {ex.message}")

            return False


async def test_manual_request():
    """Test making a manual HTTP request to see raw response."""

    print("\n🧪 Testing manual HTTP request with GET and query params...")

    ACCESS_KEY = os.getenv("ECOFLOW_ACCESS_KEY", "")
    SECRET_KEY = os.getenv("ECOFLOW_SECRET_KEY", "")
    DEVICE_SN = os.getenv("ECOFLOW_DEVICE_SN", "")

    # Generate signature manually
    timestamp = str(int(time.time() * 1000))
    nonce = str(int(time.time() * 1000000))

    params = {
        "accessKey": ACCESS_KEY,
        "nonce": nonce,
        "sn": DEVICE_SN,
        "timestamp": timestamp,
    }

    # Create signature
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params)

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    params["sign"] = signature

    url = "https://api.ecoflow.com/iot-open/sign/device/quota/all"

    print(f"📡 URL: {url}")
    print(f"📝 Query params: {params}")

    async with aiohttp.ClientSession() as session:
        try:
            # Use GET with query parameters
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, params=params, timeout=timeout) as resp:
                print(f"📊 HTTP Status: {resp.status}")
                print(f"📋 Headers: {dict(resp.headers)}")

                text = await resp.text()
                print(f"📄 Response body: {text[:500]}...")

                if resp.status == 200:
                    try:
                        json_data = await resp.json()
                        print("✅ JSON parsed successfully")
                        print(
                            f"📊 Response structure: {list(json_data.keys()) if isinstance(json_data, dict) else type(json_data)}"
                        )

                        # Show response details
                        if isinstance(json_data, dict) and json_data.get("code") == "0":
                            print("🎉 API call successful! Data received:")
                            data = json_data.get("data", {})
                            print(f"   Data keys: {list(data.keys())[:10]}...")
                        else:
                            print(
                                f"🚨 API returned error code: {json_data.get('code')} - {json_data.get('message')}"
                            )

                    except Exception as json_ex:
                        print(f"❌ Failed to parse JSON: {json_ex}")

        except Exception as ex:
            print(f"❌ HTTP request failed: {ex}")


if __name__ == "__main__":
    asyncio.run(test_ecoflow_connection())
    asyncio.run(test_manual_request())
