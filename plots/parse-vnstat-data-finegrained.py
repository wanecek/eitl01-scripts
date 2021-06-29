#!/usr/bin/env python

import argparse
import csv
import json

CSV_DELIMITER = ","


def read_json_file(fpath):
    with open(fpath, "r") as f:
        data = json.loads(f.read())
        return data["interfaces"][0]["traffic"]["fiveminute"]


def parse_timestamp(traffic_obj):
    d = traffic_obj["date"]
    t = traffic_obj["time"]
    date = "-".join(
        list(map(lambda key: str(d[key]).zfill(2), ["year", "month", "day"]))
    )
    time = str(t["hour"]).zfill(2) + ":" + str(t["minute"]).zfill(2)
    return date + " " + time + ":00+02:00"


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
                                     (five-minute)")

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

    writecsv(
        args.output_fike, [header] + traffic, delimiter=CSV_DELIMITER
    )
