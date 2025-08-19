#!/bin/bash

# This script is used to install MATLAB toolboxes into a specified MATLAB root directory.
# It supports command-line options to specify the MATLAB root directory, release version, 
# and the list of products to install. The script also provides a help message for usage guidance.

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script installs toolboxes into the specified MATLAB root directory."
    echo ""
    echo "Options:"
    echo "  -d, --destination <path>   Specify the MATLAB root directory to install into, or MATLAB on your PATH will be used."
    echo "  -r, --release <string> Specify the MATLAB release version thats already installed."
    echo "  -p, --products <list> Specify the products to install (space-separated)."
    echo "  -h                  Display this help message and exit."
    echo "  -v                  Enable verbose output."
    echo ""
    echo "Example:"
    echo '  $0 --root /path/to/matlab --products "toolbox1 toolbox2" --release "R2024b"'
    exit 0
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--destination)
            MATLAB_ROOT="$2"
            EXPLICIT_MATLAB_ROOT_PROVIDED=1
            shift 2
            ;;
        -p|--products) PRODUCTS="$2"; shift 2 ;;
        -r|--release) RELEASE="$2"; shift 2 ;;
        -v)
            VERBOSE_OUTPUT=1
            shift 1
            ;;
        -h)
            print_help
            ;;
        *)
            echo "Unknown option: $1"
            print_help
            ;;
    esac
done

# Helper function to check if verbose output is enabled
is_verbose_enabled() {
    [[ "${VERBOSE_OUTPUT:-0}" -eq 1 ]]
}

# If explicity provided MATLAB root is not set, use the default
if [ -z "${EXPLICIT_MATLAB_ROOT_PROVIDED+x}" ] || [ "$EXPLICIT_MATLAB_ROOT_PROVIDED" -ne "1" ]; then
    # If search path is not provided, use MATLAB from the system PATH if available.
    MATLAB_ON_PATH=$(which matlab)
    # Call READLINK if MATLAB_ON_PATH is not empty
    if [ -n "$MATLAB_ON_PATH" ]; then
        # Check if the MATLAB executable is on the PATH
        MATLAB_ROOT=$(readlink -f "$MATLAB_ON_PATH" | xargs dirname | xargs dirname)
    else
        # If not found, exit with an error message
        echo "Error: MATLAB not found on PATH. Either add MATLAB to the PATH or provide it using the -r flag."
        print_help
        exit 1
    fi
    if is_verbose_enabled; then
        echo "MATLAB found on PATH: $MATLAB_ROOT"
    fi
fi

# Check if MATLAB_ROOT is empty
if [ -z "$MATLAB_ROOT" ]; then
    echo "Error: MATLAB_ROOT is not set or is empty."
    exit 1
fi

# Check if MATLAB_ROOT exists
if [ ! -d "$MATLAB_ROOT" ]; then
    echo "Error: MATLAB_ROOT directory does not exist: $MATLAB_ROOT"
    exit 1
fi


## Install specified products
if [ -z "$PRODUCTS" ]; then
    echo "No products specified. Exiting."
    exit 1
fi
if [ -z "$RELEASE" ]; then
    echo "No MATLAB release specified. Exiting."
    exit 1
fi
if is_verbose_enabled; then
    echo "Installing products: $PRODUCTS"
fi

## Download MPM
wget -q https://www.mathworks.com/mpm/glnxa64/mpm && chmod +x mpm
## Install products
./mpm install  --destination "$MATLAB_ROOT" --products $PRODUCTS --release "$RELEASE" 

## Clean up
rm -f mpm
echo "Installation complete."
