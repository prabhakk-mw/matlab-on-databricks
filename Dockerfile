FROM databricksruntime/standard:15.4-LTS
## Base Layer information:
# Based on ubuntu 22.04
# Contains python3 -> python3.10 pip3(python3.11)

# By default python3 points to the python3.10 executable.
# But pip uses python3.11
# Updating the python3 to match the python used by pip
# RUN ln -fs /usr/bin/python3.11 /usr/bin/python3

ARG MATLAB_RELEASE=R2024b
ARG MATLAB_PRODUCT_LIST="MATLAB Symbolic_Math_Toolbox MATLAB_Compiler_SDK Database_Toolbox"

ENV DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC"

WORKDIR /matlab-install
RUN apt-get update && apt-get install -y \
    ca-certificates \
    git \
    unzip \
    wget \
    xvfb  \
    && git clone --depth 1 https://github.com/mathworks/devcontainer-features \
    && env RELEASE="${MATLAB_RELEASE}" PRODUCTS="${MATLAB_PRODUCT_LIST}" \
    INSTALLMATLABPROXY=true \
    INSTALLJUPYTERMATLABPROXY=true \
    INSTALLMATLABENGINEFORPYTHON=true /matlab-install/devcontainer-features/src/matlab/install.sh

# Default proxy values
ENV MWI_APP_PORT=8888
ENV MWI_BASE_URL="/matlab"
EXPOSE 8888

# For advanced options see: https://github.com/mathworks/matlab-proxy/blob/main/Advanced-Usage.md
# Enable additional logging for the proxy
#ENV MWI_LOG_LEVEL=INFO
#ENV MWI_AUTH_TOKEN=mysecuretoken
#ENV MWI_PROCESS_START_TIMEOUT=60
#ENV MWI_SHUTDOWN_ON_IDLE_TIMEOUT=60

RUN adduser --shell /bin/bash --disabled-password --gecos "" matlab \
    && echo "matlab ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/matlab \
    && chmod 0440 /etc/sudoers.d/matlab

# Work dir assumed by Databricks
WORKDIR /root