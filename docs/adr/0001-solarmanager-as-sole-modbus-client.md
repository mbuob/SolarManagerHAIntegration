# SolarManager as sole Modbus TCP client

The SolarEdge SE inverter only supports a single Modbus TCP client at a time. Running both SolarManager and Home Assistant as direct Modbus clients causes one or both to show the inverter as offline. We resolved this by designating SolarManager as the sole Modbus TCP client and having HA read from SolarManager's Local API instead of the inverter directly.

The alternative — HA as sole Modbus client with SolarManager reading from HA — was rejected because SolarManager's primary function is energy optimization and it needs direct, low-latency inverter data to do its job. HA is the better consumer in this relationship.
