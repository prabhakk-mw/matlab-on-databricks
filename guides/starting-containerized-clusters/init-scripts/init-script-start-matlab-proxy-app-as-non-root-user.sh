#!/bin/bash

sudo -u matlab env MWI_CUSTOM_HTTP_HEADERS='{"Content-Security-Policy": "frame-ancestors *"}' MWI_APP_PORT=8888 MWI_BASE_URL=/ MWI_ENABLE_TOKEN_AUTH=False matlab-proxy-app &