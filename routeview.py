#!/usr/bin/env python

import argparse
from rich.console import Console
import pexpect
import random
import requests
import re
import time
import sys

console = Console()
try:
    ArgParse = argparse.ArgumentParser()
    ArgParse.add_argument(
        "-r",
        "--prefix",
        type=str,
        required=True,
        help="Check ipv4 route in routing table",
    )
    ArgParse.add_argument(
        "-a", "--asn", type=str, required=True, help="ASN that we want to check"
    )
    ArgParse.add_argument(
        "-s", "--sleep", type=int, required=True, help="Sleep for how long"
    )
    ArgParse.add_argument(
        "--random", action="store_true", help="Pick a routeview server randomly"
    )
    ArgParse.add_argument(
        "-t",
        "--transit",
        type=str,
        required=True,
        help="A list of transit asns eg: '174,1299,3356,5511,3257,2914,7922,1221,4637,6762,12956'",
    )
    ARGS = ArgParse.parse_args()
    TRANSIT = ARGS.transit.split(",")

except Exception as e:
    console.log(repr(e))
    sys.exit(1)


def fetch_routeview():
    routeview_list = list(
        set(
            re.findall(
                "route-views\\S+.routeviews.org",
                requests.get("http://routeviews.org").text,
            )
        )
    )
    return routeview_list[random.randrange(len(routeview_list) - 1)]


def parse_routeview(output):
    filtered_output = [i for i in output.splitlines() if ARGS.asn in i]
    transit_seen = []
    peer = 0
    transit = 0
    for i in filtered_output:
        try:
            if ARGS.asn in i and "show" not in i and "Community" not in i:
                if "," in i:
                    as_path = str(i.split(",")[0]).strip()
                    index_of_asn = as_path.split().index(ARGS.asn)
                    upstream_as = as_path.split()[index_of_asn - 1]
                else:
                    index_of_asn = i.split().index(ARGS.asn)
                    upstream_as = i.split()[index_of_asn - 1]
                if upstream_as in TRANSIT:
                    transit_seen.append(upstream_as)
                    transit += 1
                else:
                    peer += 1
        except ValueError as e:
            console.log(f"fail to parse {i}\n{repr(e)}")
    if transit_seen:
        console.log(f"transit path:{transit} unique transit:{set(transit_seen)}")
    else:
        console.log("transit path:0")
    console.log(f"peering path:{peer}")


def main():
    routeview_domain = (
        "route-views.routeviews.org" if not ARGS.random else fetch_routeview()
    )
    console.log(f"connecting to {routeview_domain}")
    routeviews = pexpect.spawn(f"telnet {routeview_domain}")
    if not ARGS.random:
        routeviews.expect("Username:")
        console.log("sending username")
        routeviews.sendline("rviews")
    routeviews.expect("route-views.*>")
    console.log(f"connected to {routeview_domain}")
    routeviews.sendline("terminal length 0")
    routeviews.expect("route-views.*>")
    while True:
        routeviews.sendline(f"show ip bgp {ARGS.prefix}")
        routeviews.expect("route-views.*>")
        routeview_output = str(routeviews.before.decode("ascii"))
        if "% Network not in table" in routeview_output:
            console.log(
                "% Network not in table, you might want to try another route views server"
            )
            sys.exit(1)
        parse_routeview(routeview_output)
        time.sleep(ARGS.sleep)


if __name__ == "__main__":
    main()
