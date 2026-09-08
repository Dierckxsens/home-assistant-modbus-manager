"""Binary sensor platform."""

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import CONF_ENTITIES, ENTITY_BINARY_SENSOR
from .entity import ModbusManagerCoordinator, ModbusManagerEntity


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for definition in entry.options.get(CONF_ENTITIES, []):
        if definition["platform"] != ENTITY_BINARY_SENSOR:
            continue
        coordinator = ModbusManagerCoordinator(hass, entry.runtime_data, definition)
        await coordinator.async_config_entry_first_refresh()
        entities.append(ModbusManagerBinarySensor(coordinator, entry, definition))
    async_add_entities(entities)


class ModbusManagerBinarySensor(ModbusManagerEntity, BinarySensorEntity):
    @property
    def is_on(self):
        state = bool(self.coordinator.data)
        return not state if self.definition.get("invert", False) else state
