#!/bin/bash

## Use this init script if the user for which you want to start MATLAB is known at cluster creation time.

# Init Scripts only run at cluster creation time.
# Update this script to start MATLAB as that user.

# Update the username to the user you want to run MATLAB as

newUser="prabhakk"

echo "Updating the "matlab" user to $newUser ..."
usermod -l $newUser matlab 
sed -i -e "s/matlab/$newUser/g" /etc/passwd
mv /home/matlab /home/$newUser

sudo -H -E -u $newUser matlab-proxy-app &

## Future work:
# When a user wants to start MATLAB in a cluster, they didnt create:
# 1. He will use a notebook, to start matlab-proxy
# 2. The notebook will have to capture the appropriate username
# NOTE: Special care must be taken to strip the prohibited characters from the Databricks username Ex:('@')