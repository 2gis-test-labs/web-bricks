FROM python:3.8

FROM docker-hub.2gis.ru/ugc/e2e-python:3.8-alpine

USER root
RUN apk add --no-cache build-base musl-dev python3-dev libffi-dev openssl-dev

RUN pip3 install pip --upgrade

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY --chown=ubuntu:ubuntu . $WORKDIR

USER ubuntu

ADD . .

