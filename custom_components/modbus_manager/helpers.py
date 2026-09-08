"""Register encoding and I/O helpers."""

from __future__ import annotations

import struct

from .const import (
    DATA_FLOAT32,
    DATA_INT16,
    DATA_INT32,
    DATA_UINT16,
    DATA_UINT32,
    REGISTER_COIL,
    REGISTER_DISCRETE,
    REGISTER_HOLDING,
)


def register_count(data_type: str) -> int:
    return 1 if data_type in (DATA_UINT16, DATA_INT16) else 2


def decode_registers(registers: list[int], data_type: str, word_swap: bool = False):
    regs = list(registers)
    if word_swap and len(regs) == 2:
        regs.reverse()
    raw = b"".join(int(v).to_bytes(2, "big") for v in regs)
    formats = {
        DATA_UINT16: ">H",
        DATA_INT16: ">h",
        DATA_UINT32: ">I",
        DATA_INT32: ">i",
        DATA_FLOAT32: ">f",
    }
    return struct.unpack(formats[data_type], raw)[0]


def encode_registers(value, data_type: str, word_swap: bool = False) -> list[int]:
    formats = {
        DATA_UINT16: ">H",
        DATA_INT16: ">h",
        DATA_UINT32: ">I",
        DATA_INT32: ">i",
        DATA_FLOAT32: ">f",
    }
    raw = struct.pack(formats[data_type], value)
    regs = [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]
    if word_swap and len(regs) == 2:
        regs.reverse()
    return regs


async def read_value(unit, definition):
    """Read and scale one configured value."""
    register_type = definition["register_type"]
    address = definition["address"]
    if register_type == REGISTER_COIL:
        return (await unit.read_coils(address, 1))[0]
    if register_type == REGISTER_DISCRETE:
        return (await unit.read_discrete_inputs(address, 1))[0]

    count = register_count(definition.get("data_type", DATA_UINT16))
    if register_type == REGISTER_HOLDING:
        regs = await unit.read_holding_registers(address, count)
    else:
        regs = await unit.read_input_registers(address, count)
    raw = decode_registers(
        regs, definition.get("data_type", DATA_UINT16), definition.get("word_swap", False)
    )
    return raw * definition.get("scale", 1.0) + definition.get("offset", 0.0)


async def write_value(unit, definition, value) -> None:
    """Write one configured value."""
    if definition["register_type"] == REGISTER_COIL:
        await unit.write_coil(definition["address"], bool(value))
        return
    scale = definition.get("scale", 1.0)
    offset = definition.get("offset", 0.0)
    raw = (value - offset) / scale
    data_type = definition.get("data_type", DATA_UINT16)
    if data_type != DATA_FLOAT32:
        raw = round(raw)
    regs = encode_registers(raw, data_type, definition.get("word_swap", False))
    if len(regs) == 1:
        await unit.write_register(definition["address"], regs[0])
    else:
        await unit.write_registers(definition["address"], regs)
