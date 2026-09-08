"""Sensor platform."""

from homeassistant.components.sensor import SensorEntity

from .const import CONF_ENTITIES, ENTITY_SENSOR
from .entity import ModbusManagerCoordinator, ModbusManagerEntity


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for definition in entry.options.get(CONF_ENTITIES, []):
        if definition["platform"] != ENTITY_SENSOR:
            continue
        coordinator = ModbusManagerCoordinator(hass, entry.runtime_data, definition)
        await coordinator.async_config_entry_first_refresh()
        entities.append(ModbusManagerSensor(coordinator, entry, definition))
    async_add_entities(entities)


class ModbusManagerSensor(ModbusManagerEntity, SensorEntity):
    def __init__(self, coordinator, entry, definition):
        super().__init__(coordinator, entry, definition)
        self._attr_native_unit_of_measurement = definition.get("unit") or None

    @property
    def native_value(self):
        value = self.coordinator.data
        precision = self.definition.get("precision")
        return round(value, precision) if precision is not None and isinstance(value, float) else value
