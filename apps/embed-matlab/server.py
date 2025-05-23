# from flask import Flask, render_template, request

# app = Flask(__name__, template_folder='templates')

# @app.route('/', methods=['GET', 'POST'])
# def home():
#     url = None
#     if request.method == 'POST':
#         url = request.form.get('url')
#     return render_template('index.html', url=url)

# if __name__ == '__main__':
#     app.run(ssl_context=('cert.pem', 'key_no_password.pem'), debug=True)

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# from fastapi.middleware.cors import CORSMiddleware
# origins = [
#     "http://127.0.0.1:8000",
#     "https://127.0.0.1:8000",
#     "http://localhost:8000",
#     "https://localhost:8000",
# ]

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request, url: str = None):
    return templates.TemplateResponse("index.html", {"request": request, "url": url})

if __name__ == "__main__":
    import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile='./key_no_password.pem', ssl_certfile='./cert.pem')
    uvicorn.run(app, host="0.0.0.0", port=8000)