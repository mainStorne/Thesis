FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

RUN apt-get update
RUN apt-get install quota -y
