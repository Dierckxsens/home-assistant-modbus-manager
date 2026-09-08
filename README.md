# Home Assistant Modbus Manager

A UI-based Modbus device and register manager for Home Assistant.

> **Status:** early development (v0.1.0 MVP)

The goal is to configure Modbus devices and entities directly from the Home Assistant UI without writing YAML, while using Home Assistant's shared Modbus connection API introduced in Home Assistant 2026.9.

Initial scope:

- Modbus TCP
- Modbus RTU over TCP
- Modbus Serial RTU / ASCII
- Shared Home Assistant Modbus connections (`async_get_unit`)
- UI-created `sensor`, `binary_sensor`, `number`, and `switch` entities
- Common 16-bit and 32-bit data types with scaling
- HACS custom repository layout

This project is currently experimental. Test writeable registers carefully before using them on production equipment.
