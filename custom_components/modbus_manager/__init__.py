"""Modbus Manager integration."""

from __future__ import annotations

from modbus_connection import ModbusSerialParams, ModbusTcpParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    CONF_BAUDRATE,
    CONF_BYTESIZE,
    CONF_CONNECTION_TYPE,
    CONF_FRAMER,
    CONF_PARITY,
    CONF_STOPBITS,
    CONF_UNIT_ID,
    PLATFORMS,
    TYPE_RTU_TCP,
    TYPE_SERIAL,
)


def _params(data):
    """Build connection parameters understood by HA's shared Modbus layer."""
    if data[CONF_CONNECTION_TYPE] == TYPE_SERIAL:
        return ModbusSerialParams(
            device=data["device"],
            baudrate=data[CONF_BAUDRATE],
            bytesize=data[CONF_BYTESIZE],
            parity=data[CONF_PARITY],
            stopbits=data[CONF_STOPBITS],
            framer=data[CONF_FRAMER],
        )
    return ModbusTcpParams(
        host=data["host"],
        port=data["port"],
        framer="rtu" if data[CONF_CONNECTION_TYPE] == TYPE_RTU_TCP else "socket",
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one Modbus device/unit."""
    entry.runtime_data = async_get_unit(
        hass, entry, _params(entry.data), entry.data[CONF_UNIT_ID]
    )
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload after UI options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Modbus device."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
