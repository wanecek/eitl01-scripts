#!/usr/bin/env python

from urllib.request import urlopen, Request
import json

STELLARBEAT_API_URL = "https://api.stellarbeat.io/v1"


def count_nodes(nodes):
    active = filter(lambda node: node["active"], nodes)
    tally = {"full": 0, "basic": 0, "watcher": 0}

    for node in active:
        if node["isFullValidator"]:
            tally["full"] += 1
        elif node["isValidator"]:
            tally["basic"] += 1
        else:
            tally["watcher"] += 1

    return tally


def read_json(url):
    r = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(r) as response:
        json_content = json.loads(response.read())
        return json_content


if __name__ == "__main__":
    nodes = read_json(STELLARBEAT_API_URL)["nodes"]
    tally = count_nodes(nodes)
    total = tally["watcher"] + tally["basic"] + tally["full"]
    print(f"Results: (%d nodes)" % total)
    print("--------------------")
    print("Full Validators:", tally["full"])
    print("Basic Validators:", tally["basic"])
    print("Other:", tally["watcher"])
    print("--------------------")
