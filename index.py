#!/usr/bin/env python3
"""
index.py - Professional landing page for inactive website.
Serves a single premium HTML page with a "Download Now" button linking to Telegram.
"""

from flask import Flask, render_template_string

app = Flask(__name__)

# Inline HTML with embedded CSS for a premium, modern look
HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Inactive</title>
    <style>
        /* ----- Reset & Base ----- */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(145deg, #0b0e14 0%, #1a1f2b 100%);
            padding: 1.5rem;
            margin: 0;
        }

        /* ----- Main Card ----- */
        .card {
            max-width: 620px;
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 48px;
            padding: 3.5rem 2.5rem;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(255, 255, 255, 0.06);
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .card:hover {
            transform: translateY(-4px);
            box-shadow: 0 40px 80px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.10);
        }

        /* ----- Icon / Decoration ----- */
        .icon-wrapper {
            margin-bottom: 1.8rem;
            display: flex;
            justify-content: center;
        }

        .icon-circle {
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.8rem;
            box-shadow: 0 12px 28px rgba(245, 87, 108, 0.35);
            animation: pulse-glow 2.4s ease-in-out infinite;
        }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 12px 28px rgba(245, 87, 108, 0.35); }
            50%   { box-shadow: 0 12px 48px rgba(245, 87, 108, 0.65); }
        }

        /* ----- Typography ----- */
        h1 {
            font-size: 2.4rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: #ffffff;
            margin-bottom: 0.75rem;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        }

        .subtitle {
            font-size: 1.1rem;
            font-weight: 400;
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.6;
            margin-bottom: 2.2rem;
            max-width: 460px;
            margin-left: auto;
            margin-right: auto;
        }

        .subtitle strong {
            color: #ffffff;
            font-weight: 500;
        }

        /* ----- Download Button ----- */
        .btn-download {
            display: inline-block;
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: #0b0e14;
            font-weight: 700;
            font-size: 1.2rem;
            padding: 1rem 2.8rem;
            border-radius: 60px;
            text-decoration: none;
            letter-spacing: 0.02em;
            transition: all 0.25s ease;
            box-shadow: 0 10px 24px rgba(56, 249, 215, 0.30);
            border: none;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }

        .btn-download::after {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.4s ease;
            pointer-events: none;
        }

        .btn-download:hover {
            transform: scale(1.04);
            box-shadow: 0 16px 36px rgba(56, 249, 215, 0.50);
        }

        .btn-download:hover::after {
            opacity: 1;
        }

        .btn-download:active {
            transform: scale(0.96);
        }

        /* ----- Footer note ----- */
        .footer-note {
            margin-top: 2.2rem;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.3);
            letter-spacing: 0.3px;
        }

        .footer-note a {
            color: rgba(255, 255, 255, 0.5);
            text-decoration: none;
            transition: color 0.2s;
        }

        .footer-note a:hover {
            color: #ffffff;
        }

        /* ----- Responsive ----- */
        @media (max-width: 480px) {
            .card {
                padding: 2.5rem 1.5rem;
                border-radius: 32px;
            }
            h1 {
                font-size: 1.8rem;
            }
            .subtitle {
                font-size: 1rem;
            }
            .btn-download {
                font-size: 1rem;
                padding: 0.85rem 2rem;
                width: 100%;
            }
            .icon-circle {
                width: 64px;
                height: 64px;
                font-size: 2.2rem;
            }
        }
    </style>
</head>
<body>
    <div class="card">
        <!-- Decorative icon -->
        <div class="icon-wrapper">
            <div class="icon-circle">⛔</div>
        </div>

        <!-- Main message -->
        <h1>Website Inactive</h1>
        <p class="subtitle">
            The site is currently under maintenance.  
            Please download the <strong>Bind tool</strong> from Telegram to continue.
        </p>

        <!-- Download button -->
        <a href="https://t.me/FireXDecoder_Files_BOT?start=file_1782535741"
           class="btn-download"
           target="_blank"
           rel="noopener noreferrer">
            ⬇ Download Now
        </a>

        <!-- Small footer -->
        <div class="footer-note">
            <span>📦 Secured &bull; Official channel</span>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Render the premium landing page."""
    return render_template_string(HTML_PAGE)

@app.route('/health')
def health():
    """Simple health check for monitoring."""
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    # Run the Flask development server
    # For production, use a WSGI server like Gunicorn or Waitress.
    app.run(host='0.0.0.0', port=5000, debug=False)
