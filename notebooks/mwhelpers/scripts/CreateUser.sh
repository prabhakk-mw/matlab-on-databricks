#!/bin/bash

# This script creates the specified user if it does not exist and returns the user ID.
# If the user does not exist, it will create a new user with the specified username

print_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "This script starts MATLAB as the specified user."
    echo ""
    echo "Options:"
    echo "  -u, --user <username>   Specify the username to run MATLAB as."
    echo "  -h                      Display this help message and exit."
    echo ""
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -u|--user) USERNAME="$2"; shift ;;
        -h|--help) 
            print_help
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Check if USERNAME is provided
if [ -z "$USERNAME" ]; then
    echo "Error: No username provided. Use -u or --user to specify a username."
    exit 1
fi


if ! getent passwd $USERNAME > /dev/null; then
    adduser --shell /bin/bash --disabled-password --gecos "" $USERNAME > /dev/null \
        && echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME \
        && chmod 0440 /etc/sudoers.d/$USERNAME
fi

USER_UID=$(id -u $USERNAME)
echo "USERNAME: $USERNAME"
echo "UID: $USER_UID"
