#!/usr/bin/env bash

set -eu

DB_DIR="$HOME/sysstat-monitoring-db"


# $1 - for how long to monitor
monitor_system_stats() {
    local outfile_base
    outfile_base="$DB_DIR/$(date +%Y-%m-%d)"

    export S_COLORS="never"
    sar 1 "$1" >> "$outfile_base.sar"

    stellar_pid=$(pgrep stellar-core)
    pgsql_pid=$(pidof postgres -s)
    pids="$stellar_pid,$pgsql_pid"
    top -p "$pids" -b -n 30 -d 1 >> "$outfile_base.top"
    # Add additional newline between measurements
    echo "" >> "$outfile_base.top"
}

main() {
    if [[ ! -d "$DB_DIR" ]]; then
        mkdir -p "$DB_DIR"
    fi

    local PERIOD=1800
    local DURATION=60

    while true
    do
        local delay=$(( RANDOM % PERIOD + 1))
        sleep $delay
        monitor_system_stats "$DURATION"
        local remainder=$(( PERIOD - delay - DURATION ))
        sleep $remainder
    done
}

main
