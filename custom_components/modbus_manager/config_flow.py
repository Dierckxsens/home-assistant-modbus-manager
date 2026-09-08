"""Config flow for Modbus Manager."""

from __future__ import annotations

import uuid
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT

from .const import *

CONNECTION_TYPES = [TYPE_TCP, TYPE_RTU_TCP, TYPE_SERIAL]
DATA_TYPES = [DATA_UINT16, DATA_INT16, DATA_UINT32, DATA_INT32, DATA_FLOAT32]
REGISTER_TYPES = [REGISTER_HOLDING, REGISTER_INPUT, REGISTER_COIL, REGISTER_DISCRETE]
ENTITY_TYPES = [ENTITY_SENSOR, ENTITY_BINARY_SENSOR, ENTITY_NUMBER, ENTITY_SWITCH]


class ModbusManagerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            self._connection_type = user_input[CONF_CONNECTION_TYPE]
            return await self.async_step_serial() if self._connection_type == TYPE_SERIAL else await self.async_step_network()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_CONNECTION_TYPE, default=TYPE_TCP): vol.In(CONNECTION_TYPES)}),
        )

    async def async_step_network(self, user_input=None):
        if user_input is not None:
            data = {CONF_CONNECTION_TYPE: self._connection_type, **user_input}
            unique = f"{self._connection_type}:{data[CONF_HOST]}:{data[CONF_PORT]}:{data[CONF_UNIT_ID]}"
            await self.async_set_unique_id(unique.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data[CONF_NAME], data=data)
        return self.async_show_form(
            step_id="network",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Modbus device"): str,
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=502): vol.All(vol.Coerce(int), vol.Range(min=1, max=65535)),
                vol.Required(CONF_UNIT_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=0, max=247)),
            }),
        )

    async def async_step_serial(self, user_input=None):
        if user_input is not None:
            data = {CONF_CONNECTION_TYPE: TYPE_SERIAL, **user_input}
            unique = f"serial:{data['device']}:{data[CONF_UNIT_ID]}"
            await self.async_set_unique_id(unique.lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=data[CONF_NAME], data=data)
        return self.async_show_form(
            step_id="serial",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default="Modbus device"): str,
                vol.Required("device", default="/dev/serial/by-id/"): str,
                vol.Required(CONF_BAUDRATE, default=9600): vol.Coerce(int),
                vol.Required(CONF_BYTESIZE, default=8): vol.In([7, 8]),
                vol.Required(CONF_PARITY, default="N"): vol.In(["N", "E", "O"]),
                vol.Required(CONF_STOPBITS, default=1): vol.In([1, 2]),
                vol.Required(CONF_FRAMER, default="rtu"): vol.In(["rtu", "ascii"]),
                vol.Required(CONF_UNIT_ID, default=1): vol.All(vol.Coerce(int), vol.Range(min=0, max=247)),
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return ModbusManagerOptionsFlow(config_entry)


class ModbusManagerOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        # Home Assistant provides self.config_entry to OptionsFlow instances.
        # Do not assign to self.config_entry here; it is a managed property.
        self._options = dict(config_entry.options)
        self._platform = None

    async def async_step_init(self, user_input=None):
        return self.async_show_menu(step_id="init", menu_options=["add_entity", "remove_entity"])

    async def async_step_add_entity(self, user_input=None):
        if user_input is not None:
            self._platform = user_input["platform"]
            return await self.async_step_entity()
        return self.async_show_form(
            step_id="add_entity",
            data_schema=vol.Schema({vol.Required("platform", default=ENTITY_SENSOR): vol.In(ENTITY_TYPES)}),
        )

    async def async_step_entity(self, user_input=None):
        if user_input is not None:
            definition = {"id": uuid.uuid4().hex, "platform": self._platform, **user_input}
            entities = list(self._options.get(CONF_ENTITIES, []))
            entities.append(definition)
            self._options[CONF_ENTITIES] = entities
            return self.async_create_entry(title="", data=self._options)

        schema = {
            vol.Required("name"): str,
            vol.Required("address", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=65535)),
            vol.Required("register_type", default=REGISTER_HOLDING): vol.In(REGISTER_TYPES),
            vol.Required("data_type", default=DATA_UINT16): vol.In(DATA_TYPES),
            vol.Required("scale", default=1.0): vol.Coerce(float),
            vol.Required("offset", default=0.0): vol.Coerce(float),
            vol.Required("word_swap", default=False): bool,
            vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
        }
        if self._platform in (ENTITY_SENSOR, ENTITY_NUMBER):
            schema[vol.Optional("unit", default="")] = str
        if self._platform == ENTITY_SENSOR:
            schema[vol.Optional("precision", default=2)] = vol.All(vol.Coerce(int), vol.Range(min=0, max=6))
        if self._platform == ENTITY_BINARY_SENSOR:
            schema[vol.Required("invert", default=False)] = bool
        if self._platform == ENTITY_NUMBER:
            schema[vol.Required("min", default=0.0)] = vol.Coerce(float)
            schema[vol.Required("max", default=100.0)] = vol.Coerce(float)
            schema[vol.Required("step", default=1.0)] = vol.Coerce(float)
        return self.async_show_form(step_id="entity", data_schema=vol.Schema(schema))

    async def async_step_remove_entity(self, user_input=None):
        entities = list(self._options.get(CONF_ENTITIES, []))
        if not entities:
            return self.async_abort(reason="no_entities")
        choices = {e["id"]: f"{e['name']} ({e['platform']}, {e['address']})" for e in entities}
        if user_input is not None:
            entities = [e for e in entities if e["id"] != user_input["entity_id"]]
            self._options[CONF_ENTITIES] = entities
            return self.async_create_entry(title="", data=self._options)
        return self.async_show_form(
            step_id="remove_entity",
            data_schema=vol.Schema({vol.Required("entity_id"): vol.In(choices)}),
        )
