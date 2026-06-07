from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SolarManagerCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SolarManagerCoordinator = data["coordinator"]
    managed_devices: list[dict] = data["devices"]

    entities = []
    for device in managed_devices:
        device_id = device["deviceId"]
        device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device["name"],
            manufacturer="SolarManager",
            model=device["type"],
            via_device=(DOMAIN, entry.entry_id),
        )
        entities.append(
            SolarManagerDeviceSignalSensor(coordinator, device_id, device_info)
        )

    async_add_entities(entities)


class SolarManagerDeviceSignalSensor(
    CoordinatorEntity[SolarManagerCoordinator], BinarySensorEntity
):
    _attr_has_entity_name = True
    _attr_name = "Signal"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        device_id: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_signal"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        for device in self.coordinator.data.get("devices") or []:
            if device.get("_id") == self._device_id:
                signal = device.get("signal")
                if signal is None:
                    return None
                if isinstance(signal, bool):
                    return signal
                return str(signal).lower() == "connected"
        return None
