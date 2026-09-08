"""Base entity for Modbus Manager."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

from .const import DOMAIN
from .helpers import read_value


class ModbusManagerCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, unit, definition):
        self.unit = unit
        self.definition = definition
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name=f"Modbus Manager {definition['name']}",
            update_interval=timedelta(seconds=definition.get("scan_interval", 10)),
        )

    async def _async_update_data(self):
        return await read_value(self.unit, self.definition)


class ModbusManagerEntity(CoordinatorEntity, Entity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, definition):
        super().__init__(coordinator)
        self.entry = entry
        self.definition = definition
        self._attr_name = definition["name"]
        self._attr_unique_id = f"{entry.entry_id}_{definition['id']}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Modbus",
            model=f"Unit {entry.data['unit_id']}",
        )
