FROM python:3.7-buster

MAINTAINER Afonso Costa

WORKDIR /src

COPY . .

RUN pip install -r requirements.txt

EXPOSE 7007

ENTRYPOINT [ "python", "-m", "intrusion_monitor" ]