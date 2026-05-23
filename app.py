from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# ---------- Garena API helpers ----------
GARENA_API_BASE = "https://100067.connect.garena.com"

def garena_post(endpoint, data):
    url = f"{GARENA_API_BASE}{endpoint}"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    resp = requests.post(url, headers=headers, data=data)
    return resp.json(), resp.status_code

def garena_get(endpoint, params):
    url = f"{GARENA_API_BASE}{endpoint}"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Accept": "application/json"
    }
    resp = requests.get(url, headers=headers, params=params)
    return resp.json(), resp.status_code

# ---------- Routes ----------
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# API endpoints
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    access_token = data.get('access_token')
    if not email or not access_token:
        return jsonify({'error': 'Email and access_token required'}), 400
    payload = {
        'email': email,
        'locale': 'en_MA',
        'region': 'IND',
        'app_id': '100067',
        'access_token': access_token
    }
    result, status = garena_post('/game/account_security/bind:send_otp', payload)
    return jsonify(result), status

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    access_token = data.get('access_token')
    otp = data.get('otp')
    if not all([email, access_token, otp]):
        return jsonify({'error': 'Missing fields'}), 400
    payload = {
        'email': email,
        'app_id': '100067',
        'access_token': access_token,
        'otp': otp
    }
    result, status = garena_post('/game/account_security/bind:verify_otp', payload)
    return jsonify(result), status

@app.route('/api/bind-email', methods=['POST'])
def bind_email():
    data = request.json
    email = data.get('email')
    access_token = data.get('access_token')
    verifier_token = data.get('verifier_token')
    if not all([email, access_token, verifier_token]):
        return jsonify({'error': 'Missing fields'}), 400
    payload = {
        'app_id': '100067',
        'access_token': access_token,
        'verifier_token': verifier_token,
        'secondary_password': '91B4D142823F7D20C5F08DF69122DE43F35F057A988D9619F6D3138485C9A203',
        'email': email
    }
    result, status = garena_post('/game/account_security/bind:create_bind_request', payload)
    return jsonify(result), status

@app.route('/api/get-bind-info', methods=['GET'])
def get_bind_info():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({'error': 'access_token required'}), 400
    params = {'app_id': '100067', 'access_token': access_token}
    result, status = garena_get('/game/account_security/bind:get_bind_info', params)
    return jsonify(result), status

@app.route('/api/get-platforms', methods=['GET'])
def get_platforms():
    access_token = request.args.get('access_token')
    if not access_token:
        return jsonify({'error': 'access_token required'}), 400
    params = {'access_token': access_token}
    result, status = garena_get('/bind/app/platform/info/get', params)
    return jsonify(result), status

@app.route('/api/cancel-request', methods=['POST'])
def cancel_request():
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({'error': 'access_token required'}), 400
    payload = {'app_id': '100067', 'access_token': access_token}
    result, status = garena_post('/game/account_security/bind:cancel_request', payload)
    return jsonify(result), status

@app.route('/api/verify-identity', methods=['POST'])
def verify_identity():
    data = request.json
    email = data.get('email')
    access_token = data.get('access_token')
    otp = data.get('otp')
    secondary_password = data.get('secondary_password')
    if not email or not access_token:
        return jsonify({'error': 'email and access_token required'}), 400
    if not otp and not secondary_password:
        return jsonify({'error': 'otp or secondary_password required'}), 400
    payload = {'email': email, 'app_id': '100067', 'access_token': access_token}
    if otp:
        payload['otp'] = otp
    else:
        payload['secondary_password'] = secondary_password
    result, status = garena_post('/game/account_security/bind:verify_identity', payload)
    return jsonify(result), status

@app.route('/api/create-unbind', methods=['POST'])
def create_unbind():
    data = request.json
    access_token = data.get('access_token')
    identity_token = data.get('identity_token')
    if not access_token or not identity_token:
        return jsonify({'error': 'access_token and identity_token required'}), 400
    payload = {'app_id': '100067', 'access_token': access_token, 'identity_token': identity_token}
    result, status = garena_post('/game/account_security/bind:create_unbind_request', payload)
    return jsonify(result), status

@app.route('/api/rebind', methods=['POST'])
def rebind():
    data = request.json
    identity_token = data.get('identity_token')
    email = data.get('email')
    access_token = data.get('access_token')
    verifier_token = data.get('verifier_token')
    if not all([identity_token, email, access_token, verifier_token]):
        return jsonify({'error': 'Missing fields'}), 400
    payload = {
        'identity_token': identity_token,
        'email': email,
        'app_id': '100067',
        'verifier_token': verifier_token,
        'access_token': access_token
    }
    result, status = garena_post('/game/account_security/bind:create_rebind_request', payload)
    return jsonify(result), status

@app.route('/api/revoke-token', methods=['POST'])
def revoke_token():
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({'error': 'access_token required'}), 400
    url = f"https://100067.connect.garena.com/oauth/logout?access_token={access_token}"
    headers = {'User-Agent': 'GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)'}
    try:
        resp = requests.get(url, headers=headers)
        if resp.text.strip() == '{"result":0}':
            return jsonify({'result': 0})
        else:
            return jsonify({'result': -1, 'error': resp.text})
    except Exception as e:
        return jsonify({'result': -1, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)