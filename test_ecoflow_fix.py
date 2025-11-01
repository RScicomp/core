#!/usr/bin/env python3
"""Test the fixed EcoFlow API client."""

import asyncio
import os
import aiohttp
from homeassistant.components.ecoflow.client import EcoFlowClient


async def test_ecoflow_api():
    """Test the EcoFlow API with the corrected implementation."""
    # Use the environment variables we set earlier
    access_key = os.getenv("ECOFLOW_ACCESS_KEY", "")
    secret_key = os.getenv("ECOFLOW_SECRET_KEY", "")
    device_sn = os.getenv("ECOFLOW_DEVICE_SN", "")

    print(f"Testing EcoFlow API with:")
    print(f"  Access Key: {access_key[:8]}...{access_key[-4:]}")
    print(f"  Secret Key: {secret_key[:8]}...{secret_key[-4:]}")
    print(f"  Device SN: {device_sn}")
    print()

    async with aiohttp.ClientSession() as session:
        client = EcoFlowClient(access_key, secret_key, device_sn, session)

        try:
            print("Testing connection...")
            connection_ok = await client.async_test_connection()
            print(f"Connection test result: {connection_ok}")

            if connection_ok:
                print("\n✅ SUCCESS! Getting device data...")
                data = await client.async_get_device_quota()
                print(f"Device data keys: {list(data.keys())}")

                # Print some key metrics if available
                if "pd.soc" in data:
                    print(f"Battery level: {data['pd.soc']}%")
                if "pd.wattsOutSum" in data:
                    print(f"Power output: {data['pd.wattsOutSum']}W")
                if "pd.wattsInSum" in data:
                    print(f"Power input: {data['pd.wattsInSum']}W")

            else:
                print("\n❌ Connection test failed")

        except Exception as e:
            print(f"\n❌ Exception occurred: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_ecoflow_api())
