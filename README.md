# MATLAB on Databricks

Run MATLAB® in your Databricks® environment with this comprehensive toolkit that provides container images, initialization scripts, and utilities for seamless integration. Whether you need interactive MATLAB sessions, batch processing, or parallel computing capabilities, this repository has you covered.

## Features

- 🐳 **Custom Docker Images**: Pre-configured container images with MATLAB and Simulink® optimized for Databricks
- 🚀 **Interactive Sessions**: Access MATLAB through a web interface directly from Databricks notebooks
- ⚙️ **Initialization Scripts**: Automated setup of MATLAB and MATLAB Parallel Server™ on Databricks clusters
- 📊 **Control Panel**: User-friendly notebook interface to manage MATLAB sessions
- 🔧 **Helper Utilities**: Python modules to streamline MATLAB integration
- 📱 **Databricks Apps**: Ready-to-use applications for enhanced functionality

## Requirements

- Databricks workspace with cluster creation permissions
- MATLAB (R2024b or later recommended)
- Network License Manager for MATLAB
- Docker (for building custom containers)

## Repository Structure

| Folder | Description |
|--------|-------------|
| [`dockerfiles`](dockerfiles) | Container image definitions optimized for Databricks |
| [`init-scripts`](init-scripts) | Cluster initialization scripts for MATLAB setup |
| [`notebooks`](notebooks) | Example notebooks including the MATLAB Control Panel |
| [`apps`](apps) | Databricks Apps for extended functionality |
| [`guides`](guides) | Step-by-step instructions for common workflows |
| [`setup`](setup) | Administrator utilities for workspace configuration |

## Getting Started

1. **Build the Container Image**
   ```bash
   cd dockerfiles/matlab
   docker build -t matlab:R2025a .
   ```

2. **Configure Your Cluster**
   - Create a new Databricks cluster
   - Add the initialization scripts from [`init-scripts`](init-scripts)
   - Configure the cluster to use your custom MATLAB container

3. **Launch MATLAB**
   - Import the [`MATLAB_Control_Panel.ipynb`](notebooks/MATLAB_Control_Panel.ipynb)
   - Connect to your cluster
   - Use the control panel to start and manage MATLAB sessions

For detailed setup instructions, see our Getting Started Guide.

## Documentation

- Building Custom Containers
- Initialization Script Reference
- Databricks Apps Guide
- MATLAB Integration Workflows

## Support and Feedback

Having trouble? We'd love to help!

- Check out the [`guides`](guides) directory for detailed documentation
- Create an issue for bugs or feature requests
- See [`SECURITY.md`](SECURITY.md) for reporting security vulnerabilities

## License

See [`LICENSE.md`](LICENSE.md) for license terms and conditions.

## Required Products

- MATLAB 
- Simulink
- MATLAB Parallel Server™ (optional, for parallel computing capabilities)

Additional toolboxes can be installed as needed through the MATLAB Package Manager (MPM).

## Next Steps

Ready to get started? Head over to our Getting Started Guide to set up your first MATLAB-enabled Databricks cluster, or check out the examples folder for sample notebooks.

Note: This repository is designed for use with MathWorks products. Ensure you have appropriate licenses before use.

---------------

Copyright 2025 The MathWorks, Inc.

---------------