FROM python:3.8

FROM docker-hub.2gis.ru/ugc/e2e-python:3.8-alpine

USER root
RUN apk add --no-cache build-base

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY --chown=ubuntu:ubuntu . $WORKDIR

USER ubuntu

ADD server.py .
ENTRYPOINT python3 server.py
