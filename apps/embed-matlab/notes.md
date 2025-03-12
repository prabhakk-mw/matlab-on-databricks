Proto3 
using FastAPI instead of Flask

FastAPI uses a uvicorn which is a ASGI interface that is production ready.
Flask required the use of another production ready WSGI server.

## Databricks deployment

1. Sync local changes:
```bash
databricks sync ./proto3 /Users/prabhakk@mathworks.com/proto3 --watch
```

2. Deploy App:
```bash
databricks apps create proto3
{
  "app_status": {
    "message":"App has status: unavailable",
    "state":"UNAVAILABLE"
  },
  "compute_status": {
    "message":"App compute is running.",
    "state":"ACTIVE"
  },
  "create_time":"2024-11-14T11:50:18Z",
  "creator":"prabhakk@mathworks.com",
  "default_source_code_path":"",
  "description":"",
  "name":"proto3",
  "service_principal_id":4126327940977409,
  "service_principal_name":"app-5wj97p proto3",
  "update_time":"2024-11-14T11:52:59Z",
  "updater":"prabhakk@mathworks.com",
  "url":"https://proto3-2939132238455407.aws.databricksapps.com"
}

databricks apps deploy proto3 --source-code-path /Workspace/Users/prabhakk@mathworks.com/proto3
{
  "create_time":"2024-11-14T12:11:00Z",
  "creator":"prabhakk@mathworks.com",
  "deployment_artifacts": {
    "source_code_path":"/Workspace/Users/f370dbbd-5cf8-4841-afb4-c52dd05f2cba/src/01efa2818317120c84c03ed7b18062af"
  },
  "deployment_id":"01efa2818317120c84c03ed7b18062af",
  "mode":"SNAPSHOT",
  "source_code_path":"/Workspace/Users/prabhakk@mathworks.com/proto3",
  "status": {
    "message":"App started successfully",
    "state":"SUCCEEDED"
  },
  "update_time":"2024-11-14T12:11:03Z"
}
```






--from proto2--
The app works locally, but does not work when it is deployed within a docker container.
The reason is unknown. 

When 127.0.0.1 is accessed through a browser when the server is running in the container, then the followin g error message is displayed:

Request URL:
http://127.0.0.1:5000/
Referrer Policy:
strict-origin-when-cross-origin

proto3 will attempt to use FastAPI and uvicorn
