"""Number platform."""

from homeassistant.components.number import NumberEntity

from .const import CONF_ENTITIES, ENTITY_NUMBER
from .entity import ModbusManagerCoordinator, ModbusManagerEntity
from .helpers import write_value


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for definition in entry.options.get(CONF_ENTITIES, []):
        if definition["platform"] != ENTITY_NUMBER:
            continue
        coordinator = ModbusManagerCoordinator(hass, entry.runtime_data, definition)
        await coordinator.async_config_entry_first_refresh()
        entities.append(ModbusManagerNumber(coordinator, entry, definition))
    async_add_entities(entities)


class ModbusManagerNumber(ModbusManagerEntity, NumberEntity):
    def __init__(self, coordinator, entry, definition):
        super().__init__(coordinator, entry, definition)
        self._attr_native_min_value = definition.get("min", 0)
        self._attr_native_max_value = definition.get("max", 100)
        self._attr_native_step = definition.get("step", 1)
        self._attr_native_unit_of_measurement = definition.get("unit") or None

    @property
    def native_value(self):
        return self.coordinator.data

    async def async_set_native_value(self, value: float) -> None:
        await write_value(self.entry.runtime_data, self.definition, value)
        await self.coordinator.async_request_refresh()
