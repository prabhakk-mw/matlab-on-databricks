from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import os

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, url: str = None):
    return templates.TemplateResponse("index.html", {"request": request, "url": url})

if __name__ == "__main__":
    import uvicorn
    # Databricks apps must host HTTP servers on 0.0.0.0 and 
    # use the port number specified in the DATABRICKS_APP_PORT environment variable.
    app_port=os.environ.get("DATABRICKS_APP_PORT",8000)
    uvicorn.run(app, host="0.0.0.0", port=app_port)