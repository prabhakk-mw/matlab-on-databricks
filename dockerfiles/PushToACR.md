# Push MATLAB in Databricks Container Image to ACR

After building your container image for MATLAB in Databricks, follow these steps to push your image to the Azure Container Registry.

## Build  Image

```bash
# Builds the default image from the Dockerfile
docker build -t matlab.azurecr.io/databricks/matlab:R2025a-16.4 .
```

## Log In to ACR

1. Install [Azure CLI](https://aka.ms/acr/azure-cli) and Docker CLI on your host machine.

2. Log in to your registry.
```bash
az login
az acr login --name matlab
```

## Push Image to ACR
This step might take up to several minutes.
```bash
docker push matlab.azurecr.io/databricks/matlab:R2025a-16.4
```

## Pull Image from Databricks

1. In ACR, [Create a Token (Azure)]([Databricks secret management (Azure)](https://learn.microsoft.com/en-us/azure/databricks/security/secrets/)).
4. [Add Token Password (Azure)](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-token-based-repository-permissions#add-token-password).
5. In your Databricks workspace, enter the details of your Docker image by following the steps in [Launch Your Compute (Databricks)](https://docs.databricks.com/aws/en/compute/custom-containers#launch-your-compute-using-the-ui).

Note: For information about managing secrets and securely storing credentials in Databricks, see [Databricks secret management (Azure)](https://learn.microsoft.com/en-us/azure/databricks/security/secrets/) and [Databricks Docker Image Authentication (Azure)](https://learn.microsoft.com/en-us/azure/databricks/compute/custom-containers#auth).

