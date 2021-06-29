#!/usr/bin/env python

import argparse
from urllib.request import urlopen, Request
import json
import csv

API_URL = "https://horizon.stellar.org/ledgers?limit=200&order=desc"

def fetch_data(url):
    r = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(r) as response:
        return json.loads(response.read())


def filter_record(entry):
    return dict(
        {
            "timestamp": entry["closed_at"],
            "ops": entry["operation_count"],
            "txs": entry["successful_transaction_count"],
            "ftxs": entry["failed_transaction_count"],
        }
    )


def filter_records(entries):
    return list(map(filter_record, entries))


def record_to_list(r):
    return [r["timestamp"], r["ops"], r["txs"], r["ftxs"]]


def fetch_all_items(startdate, starturl, writer):
    url = starturl
    start_url = ""
    while True:
        response = fetch_data(url)
        print("Fetching: ", url)
        if "status" in response or (not "_embedded" in response):
            break

        entries = filter_records(response["_embedded"]["records"])
        entries = list(map(record_to_list, entries))

        writer.writerows(entries)

        beg_date = entries[0][0]
        if beg_date.startswith(startdate):
            break
        if url == API_URL:
            start_url = response["_links"]["next"]["href"]
        url = response["_links"]["next"]["href"]

    print("Started on " + start_url)
    print("Stopped on " + url)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch Horizon Ledger \
                                     activity. Saves in csv-format with \
                                     headers:\n \
                                     timestamp,operations,successful \
                                     transactions,failed transactions"
    )
    parser.add_argument(
        "output_fpath", type=str, help="path to file where to store results"
    )
    parser.add_argument(
        "--url",
        nargs=1,
        default=API_URL,
        required=False,
        help="url to start fetching activity from",
    )
    parser.add_argument(
        "--end-date",
        dest="end_date",
        nargs=1,
        required=False,
        default="2021-05-15T12",
        help="Datestamp at which to \
                        stop fetching ledger activity. Note that this is done \
                        using a simple startswith(), so it is necessary to \
                        follow the format of the Horizon JSON timestamps (e.g. \
                        2021-05-15T12)",
    )

    args = parser.parse_args()
    with open(args.output_fpath, "a+") as f:
        writer = csv.writer(f, delimiter=",")
        data = fetch_all_items(args.end_date, args.url, writer)
