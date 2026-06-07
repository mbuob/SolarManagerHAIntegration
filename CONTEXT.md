# SolarManager HA Integration

A Home Assistant custom component that reads energy data from a local SolarManager device and exposes it as HA entities, resolving a Modbus TCP single-client conflict between SolarManager and Home Assistant.

## Language

**SolarManager**:
The Swiss solar energy management device installed at the home; the sole Modbus TCP client to the inverter.
_Avoid_: gateway, bridge, proxy

**SolarEdge SE**:
The solar inverter on-site; communicates over Modbus TCP; only tolerates one connected client at a time.
_Avoid_: inverter (ambiguous if other inverters are present)

**Modbus TCP**:
The protocol used between SolarManager and the SolarEdge SE; its single-client constraint is the root cause of this integration existing.
_Avoid_: Modbus (there is no RS-485/RTU in this setup)

**Local API**:
SolarManager's HTTP(S) REST interface at `http://<host>/v2/`; the data source for this integration.
_Avoid_: SolarManager API (implies the cloud API, not the local one)

**Data Point**:
A single response from the Local API's `/v2/point` endpoint; contains instantaneous power values and Interval Energy values for the current ~10-second window.
_Avoid_: snapshot, reading, payload

**Interval Energy**:
The Wh values in a Data Point (e.g. `pWh`, `iWh`, `eWh`); represent energy transferred during the current ~10-second interval only — not a cumulative total.
_Avoid_: energy reading, watt-hour value

**Accumulated Energy**:
A running sum of Interval Energy values maintained by the component across polls; exposed as a `total_increasing` sensor for the HA Energy Dashboard.
_Avoid_: cumulative energy, total energy

**Grid Power**:
Derived instantaneous net power at the grid connection point, computed as `pW − cW + bdW − bcW`; positive means exporting to the grid, negative means importing.
_Avoid_: net power, grid import/export power (use Grid Power with sign or split into import/export sensors)

**Hub Device**:
The SolarManager unit represented as a single HA device; owns all aggregate sensors (production, consumption, grid import/export, self-consumption).
_Avoid_: SolarManager device (too generic), integration device

**Managed Device**:
One of the physical devices registered in SolarManager (Hoval WP, SolarEdge SE, Shelly 3 EM); each is represented as its own HA device with `power` and `signal` entities.
_Avoid_: sub-device, child device, peripheral

## Relationships

- The **SolarManager** is the sole **Modbus TCP** client to the **SolarEdge SE**
- The component polls the **Local API** every 10 seconds to obtain a **Data Point**
- A **Data Point** contains **Interval Energy** values and a list of **Managed Device** readings
- The component accumulates **Interval Energy** into **Accumulated Energy** for each energy dimension
- **Grid Power** is derived from fields within a **Data Point**, not read directly
- The **Hub Device** holds aggregate sensors; each **Managed Device** holds its own `power` and `signal` entities

## Example dialogue

> **Dev:** "Should I store the `pWh` value directly as the solar production sensor state?"
> **Domain expert:** "No — `pWh` is Interval Energy, only valid for the current 10-second window. You need to accumulate it into Accumulated Energy so the HA Energy Dashboard sees a rising counter."

> **Dev:** "The Shelly 3 EM shows up in `devices[]` — should its `power` replace the derived Grid Power?"
> **Domain expert:** "No. Grid Power is always derived from the top-level Data Point fields. The Shelly 3 EM is a Managed Device whose `power` entity is exposed separately for reference."

**Self-Consumption**:
Energy from PV production consumed directly on-site without transiting the grid or battery; represented by `scWh` in a Data Point.
_Avoid_: direct consumption (ambiguous with `cPvWh`)

## Flagged ambiguities

- "inverter" was used loosely — resolved: always say **SolarEdge SE** when referring to the specific device, **SolarManager** when referring to the energy management unit.
