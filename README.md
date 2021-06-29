# EITL01-scripts

A collection of scripts and resources used in a Bachelor's study on Stellar
energy consumption in the spring of 2021.

For the final report, see [its page on Lund University
Publications](http://lup.lub.lu.se/student-papers/record/9059429). There, you
can read more about the methodology.

The following scripts were used to monitor a Stellar Validator node, with the
most important part being what is contained in
[`power-monitoring`](./power-monitoring).

## Directory Structure

- `cfg` - Config files
- `power-monitoring` - systemd service for monitoring power consumption
- `sysstat-montioring` - systemd service for monitoring system resource usage

## Power monitoring

The power monitoring is managed as a system service, which calls the script
[`manager.sh`](./power-monitoring/manager.sh). The script will read the power
consumption of the machine during approximately one second in a loop with 0-5
seconds delay.

> **NOTE:** The current version of the script stores the output in
> `$HOME/power-monitoring-db` — so make sure to modify this is you want it
> somewhere else.

You may need to run `modprobe intel_rapl_msr` to enable RAPL readings. Also,
make sure that you have an awk-version that supports `asort` (e.g. `gawk` over
`mawk`).

I recommend reading up on Intel RAPL for how to interpret the results, e.g. at:

- [Issue 116](https://github.com/hubblo-org/scaphandre/issues/116) in the
  Scaphandre repo.
- “RAPL in Action: Experiences in Using RAPL for Power Measurements,” (K. N.
  Khan, M. Hirki, T. Niemi, J. K. Nurminen, and Z. Ou, ACM Trans. Model.
  Perform. Eval. Comput. Syst., vol. 3, no. 2, pp. 1–26, Apr. 2018, doi:
  [10.1145/3177754](https://dl.acm.org/doi/10.1145/3177754)).

## Sysstat monitoring

Much like the power monitoring, the sysstat monitoring runs as a system service.
When active, it will read system resource usage during 60 seconds once every
half-hour.
