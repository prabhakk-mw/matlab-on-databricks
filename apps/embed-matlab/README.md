# WebApp to Embed URL
Below is a simple example of a website that embeds a given URL into an iframe. It also includes a basic web server written in Python using the Flask framework. Make sure you have Flask installed in your environment (pip install flask).

## Step 1: Create the HTML File
Create an HTML file named index.html:

```html

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embed URL</title>
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        iframe {
            width: 80%;
            height: 80%;
            border: none;
        }
    </style>
</head>
<body>
    <iframe src="{{ url }}" allowfullscreen></iframe>
</body>
</html>
```
### Step 2: Create the Python Web Server
Create a Python file named server.py:

```python
from flask import Flask, render_template_string

app = Flask(__name__)

# Load HTML content from the file
with open('index.html', 'r') as file:
    html_content = file.read()

@app.route('/')
def home():
    # Replace 'https://example.com' with the URL you want to embed
    url_to_embed = 'https://example.com'
    return render_template_string(html_content, url=url_to_embed)

if __name__ == '__main__':
    app.run(debug=True)
```

### Step 3: Run the Web Server
Make sure you have Flask installed in your Python environment. You can install it using:


```bash
pip install flask
```

Run the server.py file:

```bash
python server.py
```
Open your web browser and go to http://127.0.0.1:5000/ to see your embedded URL.

## Note
Replace 'https://example.com' in the server.py with the URL you want to embed.
This example uses render_template_string for simplicity. For more complex projects, consider using Flask's render_template function with templates stored in a templates directory.
Ensure that the URL you are trying to embed allows embedding in iframes. Some websites have headers that prevent this for security reasons.

## Start MATLAB Proxy in a different 
env MWI_CUSTOM_HTTP_HEADERS='{"Content-Security-Policy": "frame-ancestors *"}' MWI_APP_PORT=8881  matlab-proxy-app

And then make sure that the URL is embedded in the app above.

## Start from Docker Container:
 docker run -it --rm -p 8888:8888 -e MWI_CUSTOM_HTTP_HEADERS='{"Content-Security-Policy": "frame-ancestors *"}'  mathworks/matlab:r2024b -browser

## Start MATLAB (MPA) Directly
$ matlab -externalUI
Url: 
https://127.0.0.1:31522/ui/webgui/src/index-jsd.html?snc=UA2BLV&websocket=on

Then use this URL in the server!

*This requires the flask server to be running HTTPS!*

## To generate CERTS

`openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365`


### To Remove a password
Everytime you start your flask server it will ask you for the passphrase that was used to create the cert.
This step will avoid that!

`openssl rsa -in your_private_key.pem -out new_private_key.pem `