# EITL01-scripts

A collection of scripts and resources used in Bachelor's study on Stellar energy
consumption in the spring of 2021.

The following scripts were used to monitor a Stellar Validator node, with the
most important part being what is contained in
[`power-monitoring`](./power-monitoring).

## Directory Structure

- `cfg` - Config files
- `power-monitoring` - systemd service for monitoring power consumption
- `sysstat-montioring` - systemd service for monitoring system resource usage

## Power monitoring

The power monitoring is managed as a system service, which calls the script
[`manager.sh`](./power-monitoring/manager.sh).

> **NOTE:** The current version of the script stores the output in
> `$HOME/power-monitoring-db` — so make sure to modify this is you want it
> somewhere else.

You may need to run `modprobe intel_rapl_msr` to enable rapl readings.

## Sysstat monitoring
