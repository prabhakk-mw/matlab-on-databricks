#!/bin/bash

# This script creates a new user with the specified name
# and then starts matlab-proxy-app as that user

echo "Specified User: $1"

helpFunction()
{
   echo ""
   echo "Usage: $0 -u user_to_run_as"
   echo -e "\t-u Start MATLAB as specified user"
   exit 1 # Exit script after printing help
}

while getopts "u:" opt
do
   case "$opt" in
      u ) newUser="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$newUser" ]
then
   echo "Use the -u flag to provide a user name";
   helpFunction
fi

echo "Creating $newUser ..."
usermod -l $newUser matlab 
sed -i -e "s/matlab/$newUser/g" /etc/passwd
mv /home/matlab /home/$newUser

sudo -H -E -u $newUser matlab-proxy-app &