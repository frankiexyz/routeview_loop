#!/bin/env python

import argparse
from rich.console import Console
import pexpect
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


def parse_routeview(output):
    transit_seen = []
    peer = 0
    transit = 0
    for i in output.splitlines():
        try:
            if ARGS.asn in i and "show" not in i and "Community" not in i:
                if "," in i:
                    as_path = str(i.split(",")[0]).strip()
                    index_of_asn = as_path.split().index(ARGS.asn)
                    upstream_as = as_path.split()[index_of_asn-1]
                else:
                    index_of_asn = i.split().index(ARGS.asn)
                    upstream_as = i.split()[index_of_asn-1]
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
    console.log("connecting to routeview")
    routeviews = pexpect.spawn("telnet route-views.routeviews.org")
    routeviews.expect("Username:")
    console.log("sending username")
    routeviews.sendline("rviews")
    routeviews.expect("route-views>")
    console.log("connected to routeview")
    routeviews.sendline("terminal length 0")
    routeviews.expect("route-views>")
    while True:
        routeviews.sendline(f"show ip bgp {ARGS.prefix} | include {ARGS.asn}")
        routeviews.expect("route-views>")
        parse_routeview(str(routeviews.before.decode("ascii")))
        time.sleep(ARGS.sleep)


if __name__ == "__main__":
    main()
