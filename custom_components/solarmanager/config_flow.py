from __future__ import annotations

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, CONF_HOST, CONF_API_KEY

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_API_KEY, default=""): str,
    }
)


class SolarManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> config_entries.FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api_key = user_input.get(CONF_API_KEY, "").strip() or None

            try:
                session = async_get_clientsession(self.hass)
                headers = {"X-API-Key": api_key} if api_key else {}
                async with session.get(
                    f"http://{host}/v2/point",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=8),
                ) as response:
                    response.raise_for_status()
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"SolarManager ({host})",
                    data={CONF_HOST: host, CONF_API_KEY: api_key},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
