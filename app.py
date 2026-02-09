from flask import Flask, request, Response
import requests
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    if path in ('', 'favicon.ico'):
        return "HTTP Proxy OK - Use: /http://httpbin.org/ip ou HTTP_PROXY=proxy", 200
    # Target = path as full URL (ex. /http://google.com → http://google.com)
    target = path
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target.lstrip('/')
    resp = requests.request(
        method=request.method,
        url=target,
        headers={k: v for k, v in request.headers.items() if k.lower() not in ('host', 'content-length', 'content-encoding')},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params=request.args,
        timeout=30,
        stream=True
    )
    excluded = {'content-encoding', 'content-length', 'transfer-encoding', 'connection'}
    headers = [(name.decode(), value.decode()) for name, value in resp.headers.items() if name.decode().lower() not in excluded]
    return Response(resp.iter_content(8192), resp.status_code, headers)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
