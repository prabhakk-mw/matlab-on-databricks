#!/bin/bash

#--------------------------------------------------------------------------
# (c) 2025 The MathWorks, Inc.
#--------------------------------------------------------------------------

## Install some utilitity packages to make life easier
env DEBIAN_FRONTEND='noninteractive' apt-get upgrade -y && apt-get -y install iputils-ping netcat vim 

# export MW_CONNECTOR_CONNECTION_PROFILES=noop

# Expects MATLAB to already be placed on PATH.
MATLAB_ROOT=$(readlink -f $(which matlab) | xargs dirname | xargs dirname)

# Add all the Parallel Server executables to the PATH
# Define the source directory containing the executables
PARALLEL_SERVER_BIN_DIR=$MATLAB_ROOT"/toolbox/parallel/bin"

# Loop through all files in the source directory
for file in "$PARALLEL_SERVER_BIN_DIR"/*; do
  # Check if the file is executable
  if [ -x "$file" ]; then
    # Create a symbolic link in /usr/local/bin
    ln -s "$file" /usr/local/bin/
  fi
done 

# Update MJS definition to use raw IP addresses. The hostname these machines
# are assigned are internal-only and cannot be used to reference each other.
chmod u+w $PARALLEL_SERVER_BIN_DIR/mjs_def.sh
printf "\nHOSTNAME=$DB_CONTAINER_IP\n" >> $PARALLEL_SERVER_BIN_DIR/mjs_def.sh
chmod u-w $PARALLEL_SERVER_BIN_DIR/mjs_def.sh

# Launch MJS
mjs -useonlinelicensing start

# The driver node runs the Job Manager. We also store a default profile so
# that MATLAB from workbooks picks this up by default.
if [[ $DB_IS_DRIVER = "TRUE" ]]; then
  startjobmanager
  # Defer this step to when you are using interactive MATLAB.
  # matlab -r "saveAsProfile(parallel.cluster.MJS(Host=getenv('HOSTNAME')), 'DatabricksMJS'); parallel.defaultProfile('DatabricksMJS'); exit"
fi

# Finally, launch the workers
startworker -jobmanagerhost $DB_DRIVER_IP -num 1

exit 0 # Exit cleanly
