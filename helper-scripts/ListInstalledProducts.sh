#!/bin/bash
# Copyright 2025 The MathWorks, Inc.

##
# @file ListInstalledProducts.sh
# @brief Script to list all installed MATLAB toolboxes and products.
#
# This script mimics the algorithm used by the MATLAB Command VER and
# searches for `Contents.m` files in the specified MATLAB root directory
# to identify installed MATLAB toolboxes and products. It excludes certain directories
# and ensures that MATLAB itself is listed as the top result if applicable.
#
# The script supports the following features:
# - Excludes directories such as `toolbox/local`, `toolbox/matlab`, and `mcr/`.
# - Skips folders containing `+` or `@` symbols in their paths.
# - Allows specifying a custom MATLAB root directory using the `--root` or `-r` flag.
# - Displays a summary of the results, including the number of toolboxes found, the time taken, and the root location searched.
# - Provides a help option (`-h`) to display usage information.
#
# @usage
#   ./ListInstalledProducts.sh [OPTIONS]
#
# @options
#   -r, --root <path>   Specify the MATLAB root directory to search.
#   -h                  Display help information and exit.
#
# @example
#   ./ListInstalledProducts.sh --root /path/to/matlab
#
# @note
#   Ensure that the script has execute permissions before running:
#   `chmod +x ListInstalledProducts.sh`
#
# @see
#   MATLAB documentation for the function `VER`.
##

# Default MATLAB root directory (update this path as needed)
MATLAB_ROOT="/opt/matlab/R2024b"

# Function to display help information
print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script lists all toolboxes installed in the specified MATLAB root directory."
    echo "It excludes certain directories and ensures MATLAB is listed as the top result if applicable."
    echo ""
    echo "Options:"
    echo "  -r, --root <path>   Specify the MATLAB root directory to search."
    echo "  -h                  Display this help message and exit."
    echo ""
    echo "Example:"
    echo "  $0 --root /path/to/matlab"
    exit 0
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -r|--root)
            MATLAB_ROOT="$2"
            shift 2
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

# Check if MATLAB_ROOT exists
if [ ! -d "$MATLAB_ROOT" ]; then
    echo "Error: MATLAB_ROOT directory does not exist: $MATLAB_ROOT"
    exit 1
fi

# Record the start time
start_time=$(date +%s)

# Check if MATLAB's Contents.m exists
matlab_contents="$MATLAB_ROOT/toolbox/matlab/general/Contents.m"
matlab_result=""
if [ -f "$matlab_contents" ]; then
    # Extract the first line, strip the "%" character, and trim whitespace
    matlab_result="MATLAB"
fi

# Extract MATLAB version information from VersionInfo.xml
version_info_file="$MATLAB_ROOT/VersionInfo.xml"
matlab_version="Unknown"
if [ -f "$version_info_file" ]; then
    version=$(grep -oP '(?<=<version>).*?(?=</version>)' "$version_info_file")
    release=$(grep -oP '(?<=<release>).*?(?=</release>)' "$version_info_file")
    description=$(grep -oP '(?<=<description>).*?(?=</description>)' "$version_info_file")
    matlab_version="$release $description ($version)"
fi

# Recursively search for Contents.m files, excluding specific directories and paths with + or @ symbols
results=$(find "$MATLAB_ROOT" -type f -name "Contents.m" \
    ! -path "$MATLAB_ROOT/toolbox/local/*" \
    ! -path "$MATLAB_ROOT/toolbox/matlab/*" \
    ! -path "$MATLAB_ROOT/mcr/*" \
    ! -path "*/+*" \
    ! -path "*/@*" | xargs -P "$(nproc)" -I {} bash -c '
    file="$1"
    # Read the second line of the file
    second_line=$(sed -n "2p" "$file")
    # Check if the second line starts with "% Version"
    if [[ $second_line == "% Version"* ]]; then
        # Read the first line, strip the "%" character, and trim whitespace
        sed -n "1p" "$file" | sed "s/^%//;s/^[[:space:]]*//;s/[[:space:]]*$//"
    fi
' _ {} | sort -u)

# Combine MATLAB as the top result if it exists
if [ -n "$matlab_result" ]; then
    results=$(echo -e "$matlab_result\n$results")
fi

# Record the end time
end_time=$(date +%s)

# Calculate the total time taken
elapsed_time=$((end_time - start_time))

# Count the number of unique results
num_results=$(echo "$results" | wc -l)

# Print the summary
echo "----------------------"
echo "Summary:"
echo "Root location searched: $MATLAB_ROOT"
echo "Number of results found: $num_results"
echo "MATLAB Version: $matlab_version"
echo "Total time taken: ${elapsed_time} seconds"
echo "----------------------"

# Print the unique results
echo "$results"