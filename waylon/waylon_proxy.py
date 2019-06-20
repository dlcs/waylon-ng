from flask import Flask, request, Response
import requests
import settings

app = Flask(__name__)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    manifest = request.base_url

    # manifest = manifest.replace("http", "https")
    # manifest = manifest.replace(":5000", "")

    resp = requests.get(
        url=settings.PRESLEY_BASE + "iiif/customer/manifest",
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
        params={'manifest_id': manifest})

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


if __name__ == '__main__':
    app.run()
