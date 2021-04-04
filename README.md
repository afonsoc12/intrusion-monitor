![](./res/images/server.png)

# Intrusion Monitor
[![Docker Pulls](https://img.shields.io/docker/pulls/afonsoc12/intrusion-monitor?logo=docker)](https://hub.docker.com/repository/docker/afonsoc12/intrusion-monitor)
[![PyPi Version](https://img.shields.io/pypi/v/intrusion-monitor?logo=python)](https://pypi.org/project/intrusion-monitor/)
[![Github Release](https://img.shields.io/github/v/release/afonsoc12/intrusion-monitor?logo=github)](https://github.com/afonsoc12/intrusion-monitor/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[![Github Starts](https://img.shields.io/github/stars/afonsoc12/intrusion-monitor?logo=github)](https://github.com/afonsoc12/intrusion-monitor)
[![Github Fork](https://img.shields.io/github/forks/afonsoc12/intrusion-monitor?logo=github)](https://github.com/afonsoc12/intrusion-monitor)

An SSH log watchdog, which exports failed login attempts to an InfluxDB timeseries database.

## Introduction
Exposing ports from your homelab is a potential security threat. If you monitor everything else, why not also monitor brute-force attacks to your server?

It is common to find brute-force SSH attempts, to random IP ranges and login credentials (username and password), on the most probable ports where SSH is listening,
such as port `22` (the SSH port), `2222`, and so on.

SSH login attempts are stored logged in `/var/log/auth.log`. For instance take a look at this log snippet:
```log
Mar 25 22:53:37 ubuntu sshd[26265]: Connection closed by invalid user dev 37.120.235.76 port 59304 [preauth]
Mar 25 22:54:48 ubuntu sshd[26772]: Connection closed by authenticating user root 123.56.161.195 port 44312 [preauth]
Mar 26 13:51:38 ubuntu sshd[503448]: Connection closed by 5.8.10.202 port 64319 [preauth]
Mar 27 15:50:17 ubuntu sshd[23939]: Failed password for ubnt from 106.75.246.203 port 48580 ssh2
```

None of these logins were made by me, nor I recognised these IPs. They are even from different countries!

Therefore, the aim of this tool is the following:
1. Watch your `/var/log/auth.log` for (failed) login attempts;
2. Grab the username, IP and port the attempt comes from;
3. Get IP information, latitude and longitude from [IPstack](https://ipstack.com) (you will need to register for a **free** API key [here](https://ipstack.com/signup/free));
4. Store all this information in an InfluxDB database;
5. You can then use this data to build a neat dashboards with your favourite tool (mine is [Grafana](https://grafana.com))

But the best part is that all of this runs on [Docker](https://docker.com) 🐳! 

## Operation Modes
This tool has two main operation modes:
1. Log watchdog (default):
    - The mounted log file is watched for new entries, which are then processed (extract username, IP and port, request IP information from IPstack and store in the database);
    - Supports both SSH configurations with password authentication or only public key authentication.
2. TCP socket for Rsyslog *(under development)*:
    - It listens for Rsyslog json messages in the format `{"ip": "<IP>", "username": "<username>", "port": "<port>"}`;
    - There is a great [Medium article](https://medium.com/schkn/geolocating-ssh-hackers-in-real-time-108cbc3b5665),
    that uses Rsyslog for this purpose. This offers similar functionality with a python TCP socket on a Docker container, instead of the article's node.js server;

## Docker Installation
Currently, images are supported for both `x86-64` and `arm64` architectures, so this is also suitable for your Raspberry Pi:

| Architecture<br>[![Docker Image Size](https://img.shields.io/docker/image-size/afonsoc12/intrusion-monitor/latest?logo=docker)](https://hub.docker.com/repository/docker/afonsoc12/intrusion-monitor/tags?page=1&ordering=last_updated&name=latest)| Tag<br>[![Docker Dev Version](https://img.shields.io/docker/v/afonsoc12/intrusion-monitor/latest?logo=docker)](https://hub.docker.com/repository/docker/afonsoc12/intrusion-monitor/tags?page=1&ordering=last_updated&name=latest) |
| :----: | :----: |
| x86-64 | latest |
| arm64 | latest |

There are also development images with the latest on master branch:

| Architecture<br>[![Docker Image Size](https://img.shields.io/docker/image-size/afonsoc12/intrusion-monitor/latest?logo=docker)](https://hub.docker.com/repository/docker/afonsoc12/intrusion-monitor/tags?page=1&ordering=last_updated&name=dev-latest) | Tag<br>[![Docker Dev Version](https://img.shields.io/docker/v/afonsoc12/intrusion-monitor/dev-latest?logo=docker)](https://hub.docker.com/repository/docker/afonsoc12/intrusion-monitor/tags?page=1&ordering=last_updated&name=dev-latest)|
| :----: | :----: |
| x86-64 | dev-latest |
| arm64 | dev-latest |

### Docker CLI
To create a container using the command line:
```shell
docker run -d                                        \
  --name intrusion-monitor                           \
  -e TZ=Europe/London                    `#default`  \
  -e API_KEY=<Ipstack API KEY>                       \
  -e INFLUXDB_HOST=<InfluxDB Host>                   \
  -e INFLUXDB_PORT=8086                  `#default`  \
  -e INFLUXDB_DATABASE=intrusion-monitor `#default`  \
  -e INFLUXDB_USER=                      `#optional` \
  -e INFLUXDB_PASSWORD=                  `#optional` \
  -e OPERATION_MODE=watchdog             `#default`  \
  -e LOG_LEVEL=info                      `#default`  \
  -v /var/log/auth.log:/watchdog/log/auth.log:ro     \
  afonsoc12/intrusion-monitor:latest
```

### Docker-compose

To create a standalone container with docker-compose, assuming that you have an InfluxDB instance already running:
```yaml
version: '3.5'

services:
    intrusion-monitor:
        image: afonsoc12/intrusion-monitor:latest
        container_name: intrusion-monitor
        environment:
            - TZ=Europe/London                    #default
            - API_KEY=<IPstack API key>
            - INFLUXDB_HOST=<InfluxDB host>
            - INFLUXDB_PORT=8086                  #default
            - INFLUXDB_DATABASE=intrusion-monitor #default
            - INFLUXDB_USER=                      #optional
            - INFLUXDB_PASSWORD=                  #optional
            - OPERATION_MODE=watchdog             #default
            - LOG_LEVEL=info                      #default
        volumes:
            - /var/log/auth.log:/watchdog/log/auth.log
        ports:
            - 7007:7007
        restart: unless-stopped
```

If you would like to create a stack with both [intrusion-monitor](https://github.com/afonsoc12/intrusion-monitor) and InfluxDB, you can either fork this repo or download the [docker-compose.yml`](https://github.com/afonsoc12/intrusion-monitor/blob/master/docker-compose.yml) and [`.env.sample](https://github.com/afonsoc12/intrusion-monitor/blob/master/.env.sample) files (rename the latter to `.env`).

Don't forget to edit your `.env`! Then run it with:
```shell
docker-compose -p intrusion-monitor -f docker-compose.yml --env-file .env up -d
```

### Parameters

Here are the image's parameters for ports (`-p`), environment variables (`-e`) and volume mappings (`-v`).
For docker-compose, `-p` corresponds to `ports:`, `-e` to `environment:` and `-v` to `volumes:`.

It is highly recommended that you store your environment variables, especially your secrets, in a `.env` file. You may use the [`.env.sample`](https://github.com/afonsoc12/intrusion-monitor/blob/master/.env.sample) as a template. 
If you would like to know more about environment variables in Docker, please see these articles about [Environment variables in Compose](https://docs.docker.com/compose/environment-variables/) and the [Environment file](https://docs.docker.com/compose/env-file/).

| Parameter | Mandatory? | Function | Default |
| --- | --- | --- | --- |
| `-e TZ` |  | Specify the system's timezone | Europe/London |
| `-e OPERATION_MODE` |  | Operation mode | watchdog |
| `-e API_KEY` | ✔️ |[IPstack](https://ipstack.com) API key (don't worry, its free!). | -- |
| `-e INFLUXDB_HOST` | ✔ | InfluxDB database host. It can be the container name, if both are in the same network. *See [docker-compose.yml](./docker-compose.yml)* | localhost |
| `-e INFLUXDB_PORT` |  | InfluxDB port | 8086 |
| `-e INFLUXDB_DATABASE` |  | InfluxDB database name. Creates a new one if does not exist | intrusion-monitor |
| `-e INFLUXDB_USER` |  |InfluxDB user | *optional* |
| `-e INFLUXDB_PASSWORD` |  | InfluxDB password | *optional* |
| `-e LOG_LEVEL` |  | Log level. Supports "debug" or "info" | info |
| `-p 7007:7007` |  | TCP socket port *(under development)* | -- |
| `-v /var/log/auth.log:/watchdog/log/auth.log:ro` | ✔️ <br>(in watchdog mode) | Map to the log file, in read-only mode. | *mandatory* |

<!-- 
# Grafana Dashboard
#*Under development*
#grafana-cli plugins install grafana-piechart-panel
#grafana-cli plugins install grafana-worldmap-panel
--> 

## How can I protect myself in the first place?

The first thing you can do is to disable password authentication on your machine, and opt only for public key authentication.

This method is the most secure type of authentication credentials and uses a pairs of two cryptographically secure keys: a **public key** and a **private key**. You can learn more about this in this article from [SSH.com](https://www.ssh.com/ssh/key/).

I also recommend disabling root authentication and changing the port SSH is listening to an uncommon one (don't use any of `22`, `2222`, `32222`, `52222`, and so on).

Moreover, if you have a "smart" router, configure your firewall to only allow connections from countries you are likely to access your server from, and deny everything else.

## Credits

Copyright 2021 Afonso Costa

Licensed under the Apache License, Version 2.0 (the "License");

<div>Icons made by <a href="https://www.flaticon.com/authors/creaticca-creative-agency" title="Creaticca Creative Agency">Creaticca Creative Agency</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a></div>