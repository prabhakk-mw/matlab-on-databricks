# Create MATLAB Container Image for Databricks 

Use this guide to build and customize a Docker&reg; container for using MATLAB&reg; and its toolboxes in Databricks environments.

By default, the [Dockerfile](./Dockerfile) in this folder:
1. Builds a base image of [databricksruntime/standard:16.4-LTS](https://hub.docker.com/r/databricksruntime/standard/tags)
2. Installs MATLAB and Simulink for R2025b
4. Installs Python packages for [matlab-proxy](https://github.com/mathworks/matlab-proxy), [jupyter-matlab-proxy](https://github.com/mathworks/jupyter-matlab-proxy) & [matlabengine](https://github.com/mathworks/matlab-engine-for-python)

### Requirements
* Docker

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
docker build -t matlab-on-databricks:R2025b .
```

Execute the following to test the built image:

```bash
docker run -it --rm -p 8888:8888 -u ubuntu --entrypoint /databricks/python3/bin/matlab-proxy-app matlab-on-databricks:R2025b

# Click on the printed URL on the terminal to launch the MATLAB Desktop in your browser
```

> [!NOTE]
> Databricks spins up the container for you when deployed in a cluster.

Use the [MATLAB_Control_Panel.ipynb](../../notebooks/matlab-control-panel.ipynb) notebook to interact with your container in a Databricks environment.


## Customize the Image

By default, the [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/dockerfiles/matlab/Dockerfile) installs the latest available MATLAB release without any additional toolboxes or products apart from Simulink in the `/opt/matlab/${MATLAB_RELEASE}` folder.

Use the options below to customize your build.

### Customize MATLAB Release, MATLAB Product List, MATLAB Install Location, and License Server
The [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/dockerfiles/matlab/Dockerfile) supports these Docker build-time variables:

| Argument Name | Default value | Description |
|---|---|---|
| DATABRICKS_IMAGE_TAG | 16.4-LTS | For more tags see [Databricks Runtime tags on Dockerhub](https://hub.docker.com/r/databricksruntime/standard/tags) .|
| [MATLAB_RELEASE](#build-an-image-for-a-different-release-of-matlab) | R2025b | MATLAB release to install, for example, `R2023b`.|
| [MATLAB_PRODUCT_LIST](#build-an-image-with-a-specific-set-of-products) | MATLAB | Space-separated list of products to install, for example, `MATLAB Simulink Deep_Learning_Toolbox Fixed-Point_Designer`. For more information, see [MPM.md](https://github.com/mathworks-ref-arch/matlab-dockerfile/blob/main/MPM.md).|
| [MATLAB_INSTALL_LOCATION](#build-an-image-with-matlab-installed-to-a-specific-location) | /opt/matlab/R2025b | Path to install MATLAB. |
| [LICENSE_SERVER](#build-an-image-configured-to-use-a-license-server) | *unset* | Port and hostname of the machine that is running the network license manager, using the `port@hostname` syntax. For example: `27000@MyServerName` |

Use these arguments with the the `docker build` command to customize your image.
Alternatively, you can change the default values for these arguments directly in the [Dockerfile](https://github.com/mathworks-ref-arch/matlab-on-databricks/blob/main/Dockerfile).

#### Build an Image for a Different MATLAB Release
For example, to build an image for MATLAB R2019b, use this command.
```bash
docker build --build-arg MATLAB_RELEASE=R2019b -t matlab-on-databricks:R2019b .
```

#### Build an Image with a Specific Set of Products
For example, to build an image with MATLAB and Simulink&reg;, use this command.
```bash
docker build --build-arg MATLAB_PRODUCT_LIST='MATLAB Simulink' -t matlab-on-databricks:R2025b .
```

#### Build an Image with MATLAB Installed to a Specific Location
For example, to build an image with MATLAB installed at /opt/matlab, use this command.
```bash
docker build --build-arg MATLAB_INSTALL_LOCATION='/opt/matlab' -t matlab-on-databricks:R2025b .
```

#### Build an Image Configured to Use a License Server

Including the license server information with the `docker build` command means you do not have to pass it when running the container.
```bash
# Build container with the license server.
docker build --build-arg LICENSE_SERVER=27000@MyServerName -t matlab-on-databricks:R2025b .

# Run the container without needing to pass license information.
```

If you did not provide the license server information when building the image, then provide it when running the container. Set the environment variable `MLM_LICENSE_FILE` using the `-e` flag, with the  network license manager's location in the format `port@hostname`.

```bash
# Start MATLAB, print version information, and exit.
docker run --init --rm -e MLM_LICENSE_FILE=27000@MyServerName --entrypoint=matlab matlab-on-databricks:R2025b -batch ver
```

On Databricks, you can set the `MLM_LICENSE_FILE` environment variable when creating the compute cluster.
See [Databricks Cluster Configuration](https://docs.databricks.com/aws/en/compute/configure#environment-variables) for steps on doing that.


## More MATLAB Docker Resources
* Enable additional capabilities using the [MATLAB Dependencies repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps). 
For some workflows and toolboxes, you must specify dependencies. You must do this if you want to do these tasks:
    * Install extended localization support for MATLAB
    * Play media files from MATLAB
    * Generate code from Simulink
    * Use mex functions with gcc, g++, or gfortran
    * Use the MATLAB Engine API for C and Fortran&reg;
    * Use the Polyspace&reg; 32-bit tcc compiler
    
    The [MATLAB Dependencies repository](https://github.com/mathworks-ref-arch/container-images/tree/main/matlab-deps) lists Dockerfiles for various releases and platforms. To view the Dockerfile for R2025b, click [here](https://github.com/mathworks-ref-arch/container-images/blob/main/matlab-deps/r2025b/ubuntu22.04/Dockerfile).

    These Dockerfiles contain commented lines with the libraries that support additional capabilities. Copy and uncomment these lines into your Dockerfile.
* For best practices of writing Dockerfiles for MATLAB, refer to the [MATLAB Dockerfile Reference Architecture](https://github.com/mathworks-ref-arch/matlab-dockerfile)

## Feedback
MathWorks encourages you to try this repository with your environment and provide feedback. To report a technical issue or request an enhancement, create an issue on [GitHub](https://github.com/mathworks-ref-arch/matlab-on-databricks/issues).

----

Copyright 2025 The MathWorks, Inc.

----
