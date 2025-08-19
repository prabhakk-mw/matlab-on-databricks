#!/bin/bash

# This script installs MATLAB and its dependencies on a Linux system.
# It is designed to be run as a root user.
# Usage: ./InstallMATLAB.sh <path_to_matlab_installer> <installation_directory>


# Script requires access to the internet, WGET, GIT

# Helper function to check if verbose output is enabled
is_verbose_enabled() {
    [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]
}

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script installs MATLAB and its dependencies."
    echo ""
    echo "Options:"
    echo "  -p, --products <list>   Specify the products to install (space-separated)."
    echo "  -r, --release <string>  Specify the MATLAB release version (default: R2024b)."
    echo "  -v                      Enable verbose output."
    echo "  -h                      Display this help message and exit."
    echo ""
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -p|--products) PRODUCTS="$2"; shift 2;;
        -r|--release) RELEASE="$2"; shift 2;;
        -v|--verbose) VERBOSE_OUTPUT=1; shift 1 ;;
        -h|--help) 
            print_help
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Validate required arguments
if [[ -z "$PRODUCTS" ]]; then
    if is_verbose_enabled; then
        echo "No products specified. Defaulting to MATLAB."
    fi
    PRODUCTS="MATLAB"
fi

if [[ -z "$RELEASE" ]]; then
    if is_verbose_enabled; then
        echo "Defaulting to Latest available MATLAB Release."
    fi
    RELEASE="R2024b"
fi

echo "Installing MATLAB with the following parameters:"
echo "Products: $PRODUCTS"
echo "Release: $RELEASE"

mkdir /matlab-install && cd /matlab-install

export DEBIAN_FRONTEND="noninteractive" TZ="Etc/UTC" 

env apt-get update && apt-get install -y \
    ca-certificates \
    git \
    unzip \
    wget \
    xvfb  \
    && git clone --depth 1 https://github.com/mathworks/devcontainer-features \
    && env RELEASE="${RELEASE}" PRODUCTS="${PRODUCTS}" \
    INSTALLMATLABPROXY=true \
    INSTALLJUPYTERMATLABPROXY=true \
    INSTALLMATLABENGINEFORPYTHON=true /matlab-install/devcontainer-features/src/matlab/install.sh
