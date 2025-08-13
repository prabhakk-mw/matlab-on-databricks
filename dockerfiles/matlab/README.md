# Create MATLAB Container Image for Databricks 

This repository shows you how to build and customize a Docker&reg; container for MATLAB&reg; and its toolboxes for use in Databricks environments.

By Default this [Dockerfile](./Dockerfile) builds
1. On a base image of [databricksruntime/standard:16.4-LTS](https://hub.docker.com/r/databricksruntime/standard/tags)
2. Installs MATLAB and Simulink for R2025a
4. Python packages for [matlab-proxy](https://github.com/mathworks/matlab-proxy), [jupyter-matlab-proxy](https://github.com/mathworks/jupyter-matlab-proxy) & [matlabengine](https://github.com/mathworks/matlab-engine-for-python)
5. Configure MATLAB to start in USERPATH

### Requirements
* Docker.

## Build Instructions

### Get Sources

Access the Dockerfile either by directly downloading this repository from GitHub&reg;,
or by cloning this repository and
then navigating to the appropriate folder.
```bash
git clone https://github.com/mathworks-ref-arch/matlab-on-databricks.git
cd matlab-on-databricks
```

### Build and Run Docker Image

Build container with a name and tag of your choice.
```bash
docker build -t matlab:R2025a .
```

## Customize the Image

By default, the [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/dockerfiles/matlab/Dockerfile) installs the latest available MATLAB release without any additional toolboxes or products apart from Simulink in the `/opt/matlab/${MATLAB_RELEASE}` folder.

Use the options below to customize your build.

### Customize MATLAB Release, MATLAB Product List, MATLAB Install Location, and License Server
The [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/dockerfiles/matlab/Dockerfile) supports these Docker build-time variables:

| Argument Name | Default value | Description |
|---|---|---|
| DATABRICKS_IMAGE_TAG | 16.4-LTS | For more tags see [Databricks Runtime tags on Dockerhub](https://hub.docker.com/r/databricksruntime/standard/tags) .|
| [MATLAB_RELEASE](#build-an-image-for-a-different-release-of-matlab) | R2025a | MATLAB release to install, for example, `R2023b`.|
| [MATLAB_PRODUCT_LIST](#build-an-image-with-a-specific-set-of-products) | MATLAB | Space-separated list of products to install, for example, `MATLAB Simulink Deep_Learning_Toolbox Fixed-Point_Designer`. For more information, see [MPM.md](https://github.com/mathworks-ref-arch/matlab-dockerfile/blob/main/MPM.md).|
| [MATLAB_INSTALL_LOCATION](#build-an-image-with-matlab-installed-to-a-specific-location) | /opt/matlab/R2025a | Path to install MATLAB. |
| [LICENSE_SERVER](#build-an-image-configured-to-use-a-license-server) | *unset* | Port and hostname of the machine that is running the network license manager, using the `port@hostname` syntax. For example: `27000@MyServerName` |

Use these arguments with the the `docker build` command to customize your image.
Alternatively, you can change the default values for these arguments directly in the [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/Dockerfile).

#### Build an Image for a Different MATLAB Release
For example, to build an image for MATLAB R2019b, use this command.
```bash
docker build --build-arg MATLAB_RELEASE=R2019b -t matlab:R2019b .
```

#### Build an Image with a Specific Set of Products
For example, to build an image with MATLAB and Simulink&reg;, use this command.
```bash
docker build --build-arg MATLAB_PRODUCT_LIST='MATLAB Simulink' -t matlab:R2025a .
```

#### Build an Image with MATLAB Installed to a Specific Location
For example, to build an image with MATLAB installed at /opt/matlab, use this command.
```bash
docker build --build-arg MATLAB_INSTALL_LOCATION='/opt/matlab' -t matlab:R2025a .
```

#### Build an Image Configured to Use a License Server

Including the license server information with the `docker build` command means you do not have to pass it when running the container.
```bash
# Build container with the license server.
docker build --build-arg LICENSE_SERVER=27000@MyServerName -t matlab:R2025a .

# Run the container without needing to pass license information.
docker run --init --rm matlab:R2025a -batch ver
```

## Use the Network License Manager
This container requires a network license manager to license and run MATLAB. You need either the port and hostname of the network license manager or a `network.lic` file.

**Step 1**: Contact your system administrator, who can provide one of the following:

* The address to your server, and the port it is running on, for example, `27000@MyServerName.example.com`

* A `network.lic` file containing these lines.
    ```bash
    # Sample network.lic
    SERVER MyServerName.example.com <optional-mac-address> 27000
    USE_SERVER
    ```

* A `license.dat` file. Open the `license.dat` file, find the `SERVER` line, and either extract the `port@hostname`, or create a `network.lic` file by copying the `SERVER` line and adding a `USE_SERVER` line below it.

    ```bash
    # Snippet from sample license.dat
    SERVER MyServerName.example.com <mac-address> 27000
    ```
---
**Step 2**: Use `port@hostname` or the `network.lic` file with either the `docker build` **or** the `docker run` command.

With the `docker build` command, either:

- Specify the `LICENSE_SERVER` build-arg.

    ```bash
    # Example
    docker build -t matlab:R2025a --build-arg LICENSE_SERVER=27000@MyServerName .
    ```
- Use the `network.lic` file.
    1. Place the `network.lic` file in the same folder as the Dockerfile.
    1. Uncomment the line `COPY network.lic /opt/matlab/licenses/` in the Dockerfile.
    1. Run the `docker build` command **without** the `LICENSE_SERVER` build-arg:

    ```bash
    # Example
    docker build -t matlab:R2025a .
    ```
    
With the `docker run` command, use the `MLM_LICENSE_FILE` environment variable. 

```bash
docker run --init --rm -e MLM_LICENSE_FILE=27000@MyServerName matlab:R2025a -batch ver
```

## Run the Container
If you did not provide the license server information when building the image, then provide it when running the container. Set the environment variable `MLM_LICENSE_FILE` using the `-e` flag, with the  network license manager's location in the format `port@hostname`.

```bash
# Start MATLAB, print version information, and exit.
docker run --init --rm -e MLM_LICENSE_FILE=27000@MyServerName matlab:R2025a -batch ver
```

You can run the container **without** specifying `MLM_LICENSE_FILE` if you provided the license server information when building the image, as shown in the examples below.

### Run MATLAB in an Interactive Command Prompt
To start the container and run MATLAB in an interactive command prompt, use this command.
```bash
docker run --init -it --rm matlab:R2025a
```
### Run MATLAB in Batch Mode
To start the container, run a MATLAB command, and then exit, use this command.
```bash
# Container runs the command RAND in MATLAB and exits.
docker run --init --rm matlab:R2025a -batch rand
```

### Run MATLAB with Startup Options
To override the default behavior of the container and run MATLAB with any set of arguments, such as `-logfile`, use this command.
```bash
docker run --init -it --rm matlab:R2025a -logfile "logfilename.log"
```
To learn more, see the documentation: [Commonly Used Startup Options](https://www.mathworks.com/help/matlab/matlab_env/commonly-used-startup-options.html).


## More MATLAB Docker Resources
* Explore prebuilt MATLAB Docker Containers on Docker Hub: https://hub.docker.com/r/mathworks.
    * [MATLAB Containers on Docker Hub](https://hub.docker.com/r/mathworks/matlab) hosts container images for multiple releases of MATLAB.
    * [MATLAB Deep Learning Containers on Docker Hub](https://hub.docker.com/r/mathworks/matlab-deep-learning) hosts container images with toolboxes suitable for Deep Learning.
* Enable additional capabilities using the [MATLAB Dependencies repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps). 
For some workflows and toolboxes, you must specify dependencies. You must do this if you want to do these tasks:
    * Install extended localization support for MATLAB
    * Play media files from MATLAB
    * Generate code from Simulink
    * Use mex functions with gcc, g++, or gfortran
    * Use the MATLAB Engine API for C and Fortran&reg;
    * Use the Polyspace&reg; 32-bit tcc compiler
    
    The [MATLAB Dependencies repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps) lists Dockerfiles for various releases and platforms. To view the Dockerfile for R2025a, click [here](https://github.com/mathworks-ref-arch/container-images/blob/main/matlab-deps/r2025a/ubuntu22.04/Dockerfile).

    These Dockerfiles contain commented lines with the libraries that support additional capabilities. Copy and uncomment these lines into your Dockerfile.

## Feedback
We encourage you to try this repository with your environment and provide feedback. If you encounter a technical issue or have an enhancement request, create an issue [here](https://github.com/mathworks-ref-arch/matlab-on-databricks/issues).

----

Copyright 2025 The MathWorks, Inc.

----
