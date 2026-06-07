# SolarManager HA Integration

A Home Assistant custom component that reads energy data from a local [SolarManager](https://solarmanager.ch) device via its Local API.

## Problem

Both SolarManager and Home Assistant can read energy data from a SolarEdge inverter via Modbus TCP, but the inverter only supports a single Modbus TCP client at a time. Running both causes one or both systems to show the inverter as offline or in an error state.

This integration resolves the conflict by letting SolarManager retain the sole Modbus TCP connection and having Home Assistant read from SolarManager's Local API instead.

## Features

- Polls SolarManager's `/v2/point` endpoint every 10 seconds
- Exposes instantaneous power sensors (production, consumption, grid import/export)
- Exposes accumulated energy sensors compatible with the HA Energy Dashboard
- Creates individual HA devices for each device registered in SolarManager (inverter, heat pump, smart meter, etc.)
- Marks all entities as unavailable when SolarManager is unreachable

## Requirements

- Home Assistant
- SolarManager device on the local network
- SolarManager firmware with Local API support (`/v2/point`)

## Installation

1. Copy the `custom_components/solarmanager` directory into your HA `custom_components/` folder.
2. Restart Home Assistant.
3. Go to **Settings → Devices & Services → Add Integration** and search for **SolarManager**.

## Configuration

| Parameter | Required | Description |
|---|---|---|
| `host` | Yes | IP address or hostname of the SolarManager device |
| `api_key` | No | API key for the `X-API-Key` header (if configured on the device) |
| `verify_ssl` | No | Verify SSL certificate (default: `false` — SolarManager uses a self-signed cert) |

## Entities

### Hub device (SolarManager)

| Entity | Unit | Description |
|---|---|---|
| Solar production power | W | Instantaneous PV output (`pW`) |
| Solar production energy | Wh | Accumulated PV energy (`pWh`) |
| Consumption power | W | Instantaneous home consumption (`cW`) |
| Consumption energy | Wh | Accumulated home consumption (`cWh`) |
| Grid import power | W | Instantaneous power drawn from grid (derived) |
| Grid export power | W | Instantaneous power fed to grid (derived) |
| Grid import energy | Wh | Accumulated grid import (`iWh`) |
| Grid export energy | Wh | Accumulated grid export (`eWh`) |
| Battery charge energy | Wh | Accumulated battery charging (`bcWh`) |
| Battery discharge energy | Wh | Accumulated battery discharging (`bdWh`) |
| Self-consumption energy | Wh | Accumulated direct PV consumption (`scWh`) |

### Per managed device (inverter, heat pump, smart meter, etc.)

| Entity | Description |
|---|---|
| Power | Current device power in W |
| Signal | Connection state (connected / not connected) |
| State of charge | Battery or EV charge level in % (where applicable) |

## Architecture

See [CONTEXT.md](./CONTEXT.md) for the domain glossary and [docs/adr/](./docs/adr/) for architectural decisions.
