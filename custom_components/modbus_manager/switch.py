"""Switch platform."""

from homeassistant.components.switch import SwitchEntity

from .const import CONF_ENTITIES, ENTITY_SWITCH
from .entity import ModbusManagerCoordinator, ModbusManagerEntity
from .helpers import write_value


async def async_setup_entry(hass, entry, async_add_entities):
    entities = []
    for definition in entry.options.get(CONF_ENTITIES, []):
        if definition["platform"] != ENTITY_SWITCH:
            continue
        coordinator = ModbusManagerCoordinator(hass, entry.runtime_data, definition)
        await coordinator.async_config_entry_first_refresh()
        entities.append(ModbusManagerSwitch(coordinator, entry, definition))
    async_add_entities(entities)


class ModbusManagerSwitch(ModbusManagerEntity, SwitchEntity):
    @property
    def is_on(self):
        return bool(self.coordinator.data)

    async def async_turn_on(self, **kwargs):
        await write_value(self.entry.runtime_data, self.definition, True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await write_value(self.entry.runtime_data, self.definition, False)
        await self.coordinator.async_request_refresh()
