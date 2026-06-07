from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class SolarManagerCoordinator(DataUpdateCoordinator[dict]):
    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        api_key: str | None,
    ) -> None:
        self._base_url = f"https://{host}"
        self._headers = {"X-API-Key": api_key} if api_key else {}
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        session = async_get_clientsession(self.hass, verify_ssl=False)
        try:
            async with session.get(
                f"{self._base_url}/v2/point",
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=8),
            ) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            raise UpdateFailed(f"Error fetching SolarManager data: {err}") from err

    async def async_fetch_devices(self) -> list[dict]:
        session = async_get_clientsession(self.hass, verify_ssl=False)
        async with session.get(
            f"{self._base_url}/v2/devices",
            headers=self._headers,
            timeout=aiohttp.ClientTimeout(total=8),
        ) as response:
            response.raise_for_status()
            return await response.json()
