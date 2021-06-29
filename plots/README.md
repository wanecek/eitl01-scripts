# Plotting scripts for Bachelor's thesis

> ⚠️ Here be some shaky and patched-together python scripts reading from files with
> loosely defined formats. Use at your own risk.

**NOTE:** All scripts are written for python 3.

Attempt running any script with the `-h` flag to see what arguments each script
takes.

## Getting the raw data

### Power measurements and sysstat

See parent directory.

### Network

With measurements stored in a vnstat db, I used the following commands:

For daily stats:

```bash
vnstat --begin 2021-05-13 --dbdir path/to/parent/dir/of/vnstat.db --limit 0 \
  --json d > data/vnstat/vnstat.daily.json
```

For five-minute stats:

```bash
vnstat --begin 2021-05-13 --dbdir path/to/parent/dir/of/vnstat.db --limit 0 \
  --json f > data/vnstat/vnstat.fiveminutes.json
```

These two files can then be used in the `./parse-vnstat-data.py` and
`./parse-vnstat-data-finegrained.py` scripts.
