"""Constants for Modbus Manager."""

DOMAIN = "modbus_manager"
PLATFORMS = ["sensor", "binary_sensor", "number", "switch"]

CONF_CONNECTION_TYPE = "connection_type"
CONF_UNIT_ID = "unit_id"
CONF_BAUDRATE = "baudrate"
CONF_BYTESIZE = "bytesize"
CONF_PARITY = "parity"
CONF_STOPBITS = "stopbits"
CONF_FRAMER = "framer"
CONF_ENTITIES = "entities"

TYPE_TCP = "tcp"
TYPE_RTU_TCP = "rtu_tcp"
TYPE_SERIAL = "serial"

ENTITY_SENSOR = "sensor"
ENTITY_BINARY_SENSOR = "binary_sensor"
ENTITY_NUMBER = "number"
ENTITY_SWITCH = "switch"

REGISTER_HOLDING = "holding"
REGISTER_INPUT = "input"
REGISTER_COIL = "coil"
REGISTER_DISCRETE = "discrete"

DATA_UINT16 = "uint16"
DATA_INT16 = "int16"
DATA_UINT32 = "uint32"
DATA_INT32 = "int32"
DATA_FLOAT32 = "float32"

DEFAULT_SCAN_INTERVAL = 10
