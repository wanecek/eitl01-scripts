#!/usr/bin/env python

import argparse
import csv
import json

CSV_DELIMITER = ","


def read_json_file(fpath):
    with open(fpath, "r") as f:
        data = json.loads(f.read())
        return data["interfaces"][0]["traffic"]["day"]


def parse_timestamp(traffic_obj):
    d = traffic_obj["date"]
    date = "-".join(
        list(map(lambda key: str(d[key]).zfill(2), ["year", "month", "day"]))
    )
    time = "12:00:00+02:00" # Add dummy-time since it's just daily stats
    return date + " " + time


def flatten_traffic_obj(data):
    return [
        parse_timestamp(data),
        data["rx"],
        data["tx"],
    ]


def writecsv(fpath, rows, delimiter):
    with open(fpath, "w") as f:
        writer = csv.writer(f, delimiter=delimiter)
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Parse output from vnstat json output \
                                     (daily)")

    parser.add_argument(
        "--input-file",
        nargs=1,
        help="path to JSON file with source data",
    )
    parser.add_argument(
        "--output-file",
        nargs=1,
        help="path to csv file to save results in",
    )
    args = parser.parse_args()

    traffic_data = read_json_file(args.input_file)
    traffic = list(map(flatten_traffic_obj, traffic_data))
    header = ["timestamp", "rx", "tx"]

    writecsv(args.output_file, [header] + traffic, delimiter=CSV_DELIMITER)
