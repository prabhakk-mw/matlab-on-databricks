# Pushing to ACR

## Build your Image

```bash
# Builds the default image from the Dockerfile
docker build -t matlab.azurecr.io/databricks/matlab:R2025a-16.4 .
```

## Login to ACR

Have [Azure CLI](https://aka.ms/acr/azure-cli) and Docker CLI installed locally on your host machine. Docker provides packages that easily configure Docker on any Mac OS, Windows, or Linux system.

```bash
az login
az acr login --name matlab
```

## Push your Image to ACR
This step can take a while, time to get some coffee.
```bash
docker push matlab.azurecr.io/databricks/matlab:R2025a-16.4
```

## To pull your image from Databricks

1. Navigate to your ACR's Repository Permissions Blade.
2. Click on Tokens
3. Generate a Token
4. Generate a Password for the token
5. For secure storage of the credentials in Databricks, see [Databricks Docker Image Authentication](https://learn.microsoft.com/en-us/azure/databricks/compute/custom-containers#auth).
6. Also see related [Databricks secret management](https://learn.microsoft.com/en-us/azure/databricks/security/secrets/) 

7. Finally, in Databricks, navigate to your Compute pane, and Click on the Docker section -> Select use your own image -> Select Username Password as the Authentication Mechanism -> Fill in the Token Name, Password that were generated in Step 3 & 4

