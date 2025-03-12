FROM databricksruntime/standard:15.4-LTS
## Base Layer information:
# Based on ubuntu 22.04
# Contains python3 -> python3.10 pip3(python3.11)

# By default python3 points to the python3.10 executable.
# But pip uses python3.11
# Updating the python3 to match the python used by pip
# RUN ln -fs /usr/bin/python3.11 /usr/bin/python3

ARG MATLAB_RELEASE=R2024b
ARG MATLAB_PRODUCT_LIST="MATLAB MATLAB_Parallel_Server Parallel_Computing_Toolbox"

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
# Disabling Token Authentication, as databricks already has several layers of authentication built into it.
ENV MWI_ENABLE_TOKEN_AUTH="False"
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

# The container always starts as ROOT in DBx
# To use any other user start the process using 
# sudo -u $username matlab-proxy-app

# Another Solution would be to create a new user just before attempting to start the proxy.
# This however would require that matlab-proxy is accessible globally.

# # Work dir assumed by Databricks
WORKDIR /root

# Patching the Cookie Jar version of app.py@matlab_proxy
COPY --chmod=0755 start-matlab-proxy-as-user.sh .
ADD matlab-proxy-fixed_app.py .
RUN cp matlab-proxy-fixed_app.py `python3 -m pip show matlab-proxy | grep Location | cut -d ' ' -f 2`/matlab_proxy/app.py

# docker tag prabhakk/matlab-on-databricks:r2024b matlab.azurecr.io/databricks/matlab:r2024b