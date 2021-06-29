#!/usr/bin/env python

import argparse
from pathlib import Path
import pandas

def normalize_power_consumption(series):
    duration = series["duration"]

    def normalizer(elem):
        if isinstance(elem, int):
            return elem / duration
        else:
            return elem

    return series.drop(labels=["duration"]).apply(normalizer, duration)


## Read all CSVs in basepath, and concatenate in a single csv file
def read_and_parse_csv(basepath):
    dfs = []
    header_names = ["timestamp", "duration", "CORE", "CPU", "DRAM"]
    for p in Path(basepath).glob("*.csv"):
        print("Reading", p.name, "...")
        with p.open("r") as csv_file:
            df = pandas.read_csv(
                csv_file,
                sep=";",
                header=0,
                names=header_names,
                usecols=[0, 1, 2, 3, 4],
                parse_dates=[0],
            ).apply(normalize_power_consumption, axis=1)
            dfs.append(df)
    return pandas.concat(dfs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Parse the results from power-manager and convert to power \
        consumption of CPU, CORE and RAM."
    )
    parser.add_argument(
        "--output-csv", type=str, help="path to file where to store results"
    )
    parser.add_argument(
        "--input-dir",
        nargs=1,
        help="path to directory where output from power-monitoring manager is \
        stored, e.g. './data/power-monitoring-db'",
    )

    args = parser.parse_args()

    data = read_and_parse_csv(args.input_path)
    data.to_csv(args.output_csv, index=False)
