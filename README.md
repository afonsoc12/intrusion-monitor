![](./res/images/server.png)
# Intrusion Monitor
An SSH log watchdog, which exports failed login attempts to an InfluxDB timeseries database.

## Introduction
Exposing ports from your homelab is a potential security threat. If you monitor everything else, why not monitor brute-force attacks to your server?

Often there are brute-force SSH attempts, to random IP ranges and login credentials (username and password), on the most probable ports where SSH is listenning,
such as port `22` (the SSH port), `2222`, and so on.

SSH login attempts are stored in `/var/log/auth.log`. For instance take a look at this log snippet:
```log
Mar 25 22:53:37 ubuntu sshd[26265]: Connection closed by invalid user dev 37.120.235.76 port 59304 [preauth]
Mar 25 22:54:48 ubuntu sshd[26772]: Connection closed by authenticating user root 123.56.161.195 port 44312 [preauth]
Mar 26 13:51:38 ubuntu sshd[503448]: Connection closed by 5.8.10.202 port 64319 [preauth]
Mar 27 15:50:17 ubuntu sshd[23939]: Failed password for ubnt from 106.75.246.203 port 48580 ssh2
```

None of these logins were made by me and they come from diverse countries.
The aim of this tool is the following:
1. Watch your `/var/log/auth.log` for login attempts;
2. Grab the username, IP and port the attempt comes from;
3. Get IP information, latitude and longitude from [ipstack](https://ipstack.com) (you will need to register for a **free** API key);
4. Store all this information in an InfluxDB database;
5. You can then use this data to build your neat dashbords with your favourite tool (mine is [Grafana](https://grafana.com))

But the best part is that all of this runs in [Docker](https://docker.com) 🐳! 

## Modes of Operation
This tool has two modes of operation:
1. Log watchdog (default):
    - The mounted log file is watched for new entries, which are then processed.
    - Supports both SSH configurations with password authentication or only pubkey authentication.
2. TCP socket for Rsyslog (`under development`):
    - It listens for Rsyslog json messages. There is a great Medium article [here](https://medium.com/schkn/geolocating-ssh-hackers-in-real-time-108cbc3b5665),
    but it uses a Node.js server. This offers similar functionality with a python TCP socket, in a Docker container.

## Docker Installation
Currently, images are supported for both `x86-64` and `arm64`, so this is also suitable for your Raspberry Pi:

| Architecture | Tag |
| :----: | --- |
| x86-64 | latest |
| arm64 | latest |

There are also development images with the latest on master branch:

| Architecture | Tag |
| :----: | --- |
| x86-64 | dev-latest |
| arm64 | dev-latest |

To run this container:

### Docker CLI
```shell
docker run -d 
    --name intrusion-monitor \
    -v /var/log/auth.log:/watchdog/log/auth.log:ro \
    -e TZ=Europe/London \ 
    -e API_KEY=<IPstack API KEY> \
    -e INFLUXDB_HOST= \
    -e INFLUXDB_DATABASE= \
    -e INFLUXDB_PORT= \
    -e INFLUXDB_USER= \
    -e INFLUXDB_PASSWORD= \
    -e OPERATION_MODE=watchdog # default \
    -e SSH_LOG_PATH= #Do not change, see bellow \
    -e LOG_LEVEL=info # default
```

### Docker-compose
```yaml

```

### Parameters

Here are the images parameters for ports (`-p`), environment variables (`-e`) and volume mappings (`-v`).
For docker-compose, `-p` corresponds to `ports:`, `-e` to `environment:` and `-v` to `volumes:`.

It is highly recommended that you store your environment variables, especially your secrets, in a `.env` file. You may use the `.env.sample` as a template. 
Please see these articles about [Environment variables in Compose](https://docs.docker.com/compose/environment-variables/) and the [Environment file](https://docs.docker.com/compose/env-file/).

| Parameter | Mandatory? | Function | Default |
| --- | --- | --- | --- |
| `-p 7007:7007` |  | TCP socket port *(under development)* | -- |
| `-e TZ` |  | Specify your timezone | Europe/London |
| `-e OPERATION_MODE` |  | Operation mode | watchdog |
| `-e API_KEY` | ✔️ |Ipstacks API key (don't wirry, its free!). | -- |
| `-e INFLUXDB_HOST` | ✔<br>(with docker)️ | InfluxDB database host. It can be the container name, if both are in the same network. *See [docker-compose.yml](./docker-compose.yml)* | localhost |
| `-e INFLUXDB_PORT` |  | InfluxDB portternal subnet for the wireguard and server and peers (only change if it clashes). Used in server mode. | 8086 |
| `-e INFLUXDB_DATABASE` |  | InfluxDB database name. Creates a new one if does not exist | intrusion-monitor |
| `-e INFLUXDB_USER` |  |InfluxDB user | *optional* |
| `-e INFLUXDB_PASSWORD` |  | InfluxDB password | *optional* |
| `-e LOG_LEVEL` |  | Log level: supports "debug" or "info" | info |
| `-v /var/log/auth.log:/watchdog/log/auth.log:ro` | ✔️<br>(in watchdog mode) | Map to the log file, in read-only mode. | *mandatory* |

<!-- 
# Grafana Dashboard
#*Under development*
#grafana-cli plugins install grafana-piechart-panel
#grafana-cli plugins install grafana-worldmap-panel
--> 

## How can I protect myself in the first place?

The first thing you can do is to disable password authentication on your machine, and opt only for public key authentication.

This method is the most secure type of authentication credentials and uses a pairs of two cryptographically secure keys: a public key and a private key. You can learn more about this in this article from [SSH.com](https://www.ssh.com/ssh/key/).

I also recommend disabling root authentication and changing the port SSH is listening to an uncommon one (don't use any of `22`, `2222`, `32222`, `52222`, and so on).

Moreover, if you have a "smart" router, configure your firewall to only allow connections from countries you are likely to access your server from, and deny everything else.


## Credits

Copyright 2021 Afonso Costa

Licensed under the Apache License, Version 2.0 (the "License");

<div>Icons made by <a href="https://www.flaticon.com/authors/creaticca-creative-agency" title="Creaticca Creative Agency">Creaticca Creative Agency</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>