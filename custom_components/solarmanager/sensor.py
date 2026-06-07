from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy, UnitOfPower, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SolarManagerCoordinator


@dataclass(frozen=True, kw_only=True)
class SolarManagerSensorDescription(SensorEntityDescription):
    field_key: str = ""


HUB_POWER_SENSORS: tuple[SolarManagerSensorDescription, ...] = (
    SolarManagerSensorDescription(
        key="solar_production_power",
        name="Solar Production Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        field_key="pW",
    ),
    SolarManagerSensorDescription(
        key="consumption_power",
        name="Consumption Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        field_key="cW",
    ),
    SolarManagerSensorDescription(
        key="battery_charge_power",
        name="Battery Charge Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        field_key="bcW",
    ),
    SolarManagerSensorDescription(
        key="battery_discharge_power",
        name="Battery Discharge Power",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        field_key="bdW",
    ),
)

HUB_ENERGY_SENSORS: tuple[SolarManagerSensorDescription, ...] = (
    SolarManagerSensorDescription(
        key="solar_production_energy",
        name="Solar Production Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="pWh",
    ),
    SolarManagerSensorDescription(
        key="consumption_energy",
        name="Consumption Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="cWh",
    ),
    SolarManagerSensorDescription(
        key="battery_charge_energy",
        name="Battery Charge Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="bcWh",
    ),
    SolarManagerSensorDescription(
        key="battery_discharge_energy",
        name="Battery Discharge Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="bdWh",
    ),
    SolarManagerSensorDescription(
        key="grid_import_energy",
        name="Grid Import Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="iWh",
    ),
    SolarManagerSensorDescription(
        key="grid_export_energy",
        name="Grid Export Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="eWh",
    ),
    SolarManagerSensorDescription(
        key="self_consumption_energy",
        name="Self-Consumption Energy",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        field_key="scWh",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: SolarManagerCoordinator = data["coordinator"]
    managed_devices: list[dict] = data["devices"]

    hub_device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="SolarManager",
        manufacturer="SolarManager",
    )

    entities: list[SensorEntity] = []

    for description in HUB_POWER_SENSORS:
        entities.append(
            SolarManagerPowerSensor(coordinator, description, hub_device_info, entry.entry_id)
        )

    entities.append(SolarManagerGridImportPowerSensor(coordinator, hub_device_info, entry.entry_id))
    entities.append(SolarManagerGridExportPowerSensor(coordinator, hub_device_info, entry.entry_id))

    for description in HUB_ENERGY_SENSORS:
        entities.append(
            SolarManagerAccumulatedEnergySensor(coordinator, description, hub_device_info, entry.entry_id)
        )

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
            SolarManagerDevicePowerSensor(coordinator, device_id, device_info)
        )
        if device["type"] in ("battery", "car"):
            entities.append(
                SolarManagerDeviceSocSensor(coordinator, device_id, device_info)
            )

    async_add_entities(entities)


class SolarManagerPowerSensor(CoordinatorEntity[SolarManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        description: SolarManagerSensorDescription,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.field_key)


class SolarManagerGridImportPowerSensor(CoordinatorEntity[SolarManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Grid Import Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_grid_import_power"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        d = self.coordinator.data
        grid = (d.get("pW") or 0) - (d.get("cW") or 0) + (d.get("bdW") or 0) - (d.get("bcW") or 0)
        return max(0.0, -grid)


class SolarManagerGridExportPowerSensor(CoordinatorEntity[SolarManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Grid Export Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_grid_export_power"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        d = self.coordinator.data
        grid = (d.get("pW") or 0) - (d.get("cW") or 0) + (d.get("bdW") or 0) - (d.get("bcW") or 0)
        return max(0.0, grid)


class SolarManagerAccumulatedEnergySensor(
    CoordinatorEntity[SolarManagerCoordinator], RestoreSensor
):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        description: SolarManagerSensorDescription,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info
        self._accumulated: float = 0.0

    async def async_added_to_hass(self) -> None:
        # Restore accumulated total before subscribing so the first coordinator
        # update adds on top of the correct baseline, not zero.
        if (last_data := await self.async_get_last_sensor_data()) is not None:
            try:
                self._accumulated = float(last_data.native_value or 0)
            except (ValueError, TypeError):
                self._accumulated = 0.0
        await super().async_added_to_hass()

    def _handle_coordinator_update(self) -> None:
        if self.coordinator.data is not None:
            interval_wh = self.coordinator.data.get(self.entity_description.field_key) or 0
            if interval_wh > 0:
                self._accumulated += interval_wh
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        return self._accumulated


class SolarManagerDevicePowerSensor(CoordinatorEntity[SolarManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "Power"
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        device_id: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_power"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None:
            return None
        for device in self.coordinator.data.get("devices") or []:
            if device.get("_id") == self._device_id:
                return device.get("power")
        return None


class SolarManagerDeviceSocSensor(CoordinatorEntity[SolarManagerCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_name = "State of Charge"
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: SolarManagerCoordinator,
        device_id: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._device_id = device_id
        self._attr_unique_id = f"{device_id}_soc"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        for device in self.coordinator.data.get("devices") or []:
            if device.get("_id") == self._device_id:
                return device.get("soc")
        return None
