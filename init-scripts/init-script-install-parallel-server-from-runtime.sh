#!/bin/bash
#--------------------------------------------------------------------------
# MATLAB runtime installation Databricks init script
#
# The script requires that two environment variables are defined, e.g:
#
#   MW_RUNTIME_ZIP=/Volumes/mycatalog/myschema/myvolume/MathWorks/Runtimes/MATLAB_Runtime_R2024a_Update_5_glnxa64.zip
#
#   LD_LIBRARY_PATH=/MATLAB_Runtime/runtime/glnxa64:
#                   /MATLAB_Runtime/bin/glnxa64:
#                   /MATLAB_Runtime/sys/os/glnxa64:
#                   /MATLAB_Runtime/extern/bin/glnxa64:
#                   /MATLAB_Runtime/sys/opengl/lib/glnxa64
#
# MW_RUNTIME_ZIP provides the path or HTTP url from which to copy the .zip form of
# the MATLAB runtime. Download locations for the runtime .zip file can be specified
# as a POSIX style path corresponding to the volume or a HTTP(S) URL.
#
# The version of the MATLAB runtime used MUST match the version of MATLAB used
# to compile MATLAB code to be executed on a Databricks cluster as a library.
#
# MATLAB runtimes can be downloaded from:
#    https://www.mathworks.com/products/compiler/matlab-runtime.html
# Note that only the Linux version can be used on a Databricks cluster
# For supported versions see: Documentation/SupportMatrix.md
#
# If the installation otherwise fails a non zero value is returned which will be
# interpreted by Databricks as a failure to initialize the cluster.
#
# If init scripts are not the preferred way to provision a MATLAB enabled cluster,
# Docker can be used see: Documentation/DockerRuntimes.md
# See also: Documentation/InitScripts.md
#
# The runtime .zip file is large, > 4GB, and should be located in a cloud storage
# environment that is fast and close to the cluster deployment location. Otherwise
# cluster deployment will be slow and can timeout.
#
# Invocation of this script to install a runtime assumes agreement to the terms
# of the runtime's license.
#
# See also: https://docs.databricks.com/en/init-scripts/index.html
#
# (c) 2021-2024 The MathWorks, Inc.
#
# Last updated in version 5.0.0
#
#--------------------------------------------------------------------------

# Install the MATLAB Runtime using the silent installation method
echo "MATLAB runtime installation"
echo "==========================="

echo "Reporting environment:"
printenv | sort

echo "    MW_RUNTIME_ZIP: $MW_RUNTIME_ZIP"

# By default do not accept the runtime(s) license(s) this may be updated to yes
# during the installation process prior to uploading to Databricks
agreeToLicense=yes
echo "    agreeToLicense: $agreeToLicense"

unset LD_LIBRARY_PATH
export MW_CONNECTOR_CONNECTION_PROFILES=noop

# First install libgbm1 and libnss3, which are needed for Simulink Compiler
DEBIAN_FRONTEND="noninteractive" # Stops apt asking interactive questions
apt-get update -q -o APT::Update::Error-Mode=any -o Dir::Etc::SourceParts=/tmp/nonexistantDir
if [[ $? -ne 0 ]]; then
    echo "Error apt-get update failed, check internet access" >&2
    echo "libgbm1 libnss3 cannot be automatically installed" >&2
    echo "These libraries are required by compiled Simulink code" >&2
    echo "See Documentation/InitScripts.md for details" >&2
else
    apt-get -q install -y libgbm1 libnss3
    if [[ $? -ne 0 ]]; then
        echo "Could not install libgbm1 and libnss3" >&2
        echo "These libraries are required by compiled Simulink code" >&2
        echo "See Documentation/InitScripts.md for details" >&2
    fi
fi

# Print the type of the node
if [[ $DB_IS_DRIVER == "TRUE" ]]; then
    echo "Running on Driver node"
else
    echo "Running on Worker node"
fi

# If the zip location string is a http url
# Split based on a ? e.g. to strip off a SAS after the file
# Get the zeroth field, i.e. the file part of the url
# Use basename to extract the file from that
# Build a destination path and download with curl to that
if [[ "$MW_RUNTIME_ZIP" == http* ]]; then
    IFS='?'
    read -a STRARRAY <<< "$MW_RUNTIME_ZIP"
    BASEURL="${STRARRAY[0]}"
    RUNTIMEFILE=$(basename $BASEURL)
    RUNTIMEPATH=/tmp/${RUNTIMEFILE}
    curl -o /tmp/parallel_server.zip "${MW_RUNTIME_ZIP}"
else
    # MW_RUNTIME_ZIP is location of where the zip file can be found
    cp ${MW_RUNTIME_ZIP} /tmp/parallel_server.zip
fi
CPRETURN=$?;
if [ "$CPRETURN" -ne 0 ]; then
  echo "Copy of MATLAB runtime failed, returned: ${CPRETURN}" >&2
  exit "$CPRETURN"
fi 

# Unzip to a clean temporary location
echo "Unzipping runtime"
unzip -q  /tmp/parallel_server.zip -d /MATLAB_Parallel_server
ZIPRETURN=$?;
if [ "$ZIPRETURN" -ne 0 ]; then
  echo "unzip of MATLAB runtime failed, returned: ${ZIPRETURN}" >&2
  exit "$ZIPRETURN"
fi
echo "Deleting /tmp/parallel_server.zip"
rm /tmp/parallel_server.zip

ln -s /MATLAB_Parallel_server/R2024b_parallel_server/bin/matlab /usr/local/bin/matlab

# Update MJS definition to use raw IP addresses. The hostname these machines
# are assigned are internal-only and cannot be used to reference each other.
chmod u+w /MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/mjs_def.sh
printf "\nHOSTNAME=$DB_CONTAINER_IP\n" >> /MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/mjs_def.sh
chmod u-w /MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/mjs_def.sh

# Launch MJS
/MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/mjs start

# The driver node runs the Job Manager. We also store a default profile so
# that MATLAB from workbooks picks this up by default.
if [[ $DB_IS_DRIVER = "TRUE" ]]; then
  /MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/startjobmanager
  /MATLAB_Parallel_server/R2024b_parallel_server/bin/matlab -r "saveAsProfile(parallel.cluster.MJS(Host=getenv('HOSTNAME')), 'DatabricksMJS'); parallel.defaultProfile('DatabricksMJS'); exit"
fi

# Finally, launch the workers
/MATLAB_Parallel_server/R2024b_parallel_server/toolbox/parallel/bin/startworker -jobmanagerhost $DB_DRIVER_IP -num 4

exit 0 # Exit cleanly
