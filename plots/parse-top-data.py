#!/usr/bin/env python

import argparse
import os
import re
import sys

def chunk_csv_header():
    return [
        "timestamp",
        "CPU US",
        "CPU SY",
        "CPU ID",
        "MEM USED",
        "MEM BUFF",
        "Stellar CPU%",
        "Stellar MEM%",
        "PGSQL CPU%",
        "PGSQL MEM%",
    ]

def csv_rows_generator(lines):
    if not lines:
        return

    row = lines.pop()
    while not row.startswith("top"):
        if not lines: return

        row = lines.pop().strip()

    yield row.split(" ")[2]

    while not row.startswith("%Cpu"):
        row = lines.pop().strip()

    cpu_stats = row.split("  ")
    cpu_us = cpu_stats[1].split(" ")[0]
    cpu_sy = cpu_stats[2].split(" ")[0]
    cpu_id = cpu_stats[4].split(" ")[0]

    yield cpu_us
    yield cpu_sy
    yield cpu_id

    while not row.startswith("MiB Mem"):
        row = lines.pop().strip()

    mem = row.split("  ")
    mem_used = mem[2].strip().split(" ")[0]
    mem_buff = mem[4].strip().split(" ")[0]

    yield mem_used
    yield mem_buff

    while not "PID" in row:
        row = lines.pop().strip()

    procs = []
    while not row.startswith("top") and lines:
        row = lines.pop().strip()
        if not row.startswith("top"):
            procs.append(row)

    lines.append(row)

    stellar = next(filter(lambda x: "stellar" in x, procs), None)
    postgres = next(filter(lambda x: "postgres" in x, procs), None)

    if stellar:
        stellar = re.split(r'\s+', stellar.strip())
        stellar_cpu = stellar[8]
        stellar_mem = stellar[9]
        yield stellar_cpu
        yield stellar_mem
    else :
        yield ""
        yield ""

    if postgres:
        postgres = re.split(r'\s+', postgres.strip())
        postgres_cpu = postgres[8]
        postgres_mem = postgres[9]
        yield postgres_cpu
        yield postgres_mem
    else :
        yield ""
        yield ""

def read_top_file(fpath, delimiter = ','):
    with open(fpath, 'r') as f:
        lines = f.readlines()
        lines.reverse()

        entries = []
        while len(lines) > 0:
            gen = csv_rows_generator(lines)
            row = delimiter.join([x for x in gen])
            entries.append(row)
        return entries

def is_valid_file(fpath):
    return os.path.isfile(fpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Parse output from top files, printed to \
                                     stdout")

    parser.add_argument(
        "--input-files",
        nargs="+",
        required=True,
        help="List of files to take as input",
    )
    args = parser.parse_args()
    input_files = list(filter(is_valid_file, args.input_files))

    DELIM = ","

    print(DELIM.join(chunk_csv_header()))

    if len(input_files) > 0:
        for fpath in input_files:
            csv_rows = read_top_file(fpath, DELIM)
            date = fpath.split("/")[-1].split(".")[0]
            for r in csv_rows:
                print(date + " " + r)

    else:
        print("Expected at least one file as argument")
