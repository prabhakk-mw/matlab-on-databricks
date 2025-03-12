# Databricks Apps
This folder lists various examples of Apps that can be used with Databricks Apps

Note: Databricks Apps are still in Public Preview

```markdown
Important rules about Apps:
* Databricks Apps send a SIGKILL signal 15 seconds after a SIGTERM, so apps should gracefully shut down no more than 15 seconds after receiving the SIGTERM signal. If an app has not exited after 15 seconds, a SIGKILL signal is sent to terminate the process and all child processes.
Because Databricks Apps are run as a non-privileged system user, they cannot perform operations that require running in a privileged security context, such as operations requiring root user permissions.

* Requests are forwarded from a reverse proxy, so apps must not depend on the origins of the requests. The Databricks Apps environment sets the required configuration parameters for supported frameworks.

* Because the Databricks app framework manages Transport Layer Security (TLS) connections, your apps must not perform any TLS connection or handshake operations.

* Your apps must be implemented to handle requests in HTTP/2 cleartext (H2C) format.
Databricks apps must host HTTP servers on 0.0.0.0 and use the port number specified in the DATABRICKS_APP_PORT environment variable. See environment variables: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/configuration#env-variables.

```
Taken from : https://docs.databricks.com/aws/en/dev-tools/databricks-apps/app-development#important-guidelines-for-implementing-databricks-apps


## Databricks Apps environment variables
The following variables are automatically set in the Databricks Apps environment and available to all apps.
If you need to set additional environment variables, add them to the `app.yaml` file.

| Variable | Description |
|--|--|
| DATABRICKS_APP_NAME | The name of the running app. |
| DATABRICKS_WORKSPACE_ID | The unique ID for the Databricks workspace the app belongs to. |
| DATABRICKS_HOST | The URL of the Databricks workspace to which the app belongs. |
| DATABRICKS_APP_PORT | The network port the app should listen on. |
| DATABRICKS_CLIENT_ID | The client ID for the Databricks service principal assigned to the app. |
| DATABRICKS_CLIENT_SECRET | The OAuth secret for the Databricks service principal assigned to the app. |