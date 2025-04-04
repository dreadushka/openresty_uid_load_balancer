from flask import Flask, request, jsonify
import os

app = Flask(__name__)

INSTANCE_NUMBER = os.getenv('INSTANCE_NUMBER', 'unknown')

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def catch_all(path):
    request_info = {
        'instance_number': INSTANCE_NUMBER,
        'method': request.method,
        'url': request.url,
        'path': request.path,
        'headers': dict(request.headers),
        'args': request.args.to_dict(),
        'form_data': request.form.to_dict(),
        'json_data': request.get_json(silent=True),
        'remote_addr': request.remote_addr,
        'endpoint': request.endpoint,
        'blueprint': request.blueprint,
        'cookies': request.cookies.to_dict(),
        'is_secure': request.is_secure,
        'scheme': request.scheme,
        'host': request.host,
        'content_length': request.content_length,
        'content_type': request.content_type,
        'mimetype': request.mimetype,
        'query_string': request.query_string.decode('utf-8')
    }
    return jsonify(request_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
