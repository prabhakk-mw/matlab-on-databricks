# FROM databricksruntime/standard:15.4-LTS
FROM ubuntu:latest

USER root

# Install python3
ENV DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC"

WORKDIR /matlab-install
RUN apt-get update && apt-get install -y \
    python3 python3-venv 

WORKDIR /proxy-app
COPY . /proxy-app

SHELL ["/bin/bash", "-c"]
RUN python3 -m venv . \
    && source ./bin/activate \
    && python3 -m pip install fastapi uvicorn jinja2

# Server Runs on this port
EXPOSE 5000

ENTRYPOINT [ "/proxy-app/bin/python3" , "/proxy-app/server.py" ]



