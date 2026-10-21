import os
from urllib.parse import urlsplit

import requests
from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

# Existing Meta webhook settings. Keep their values in Railway Variables.
PAGEACCESSTOKEN = os.getenv("PAGEACCESSTOKEN")
VERIFYTOKEN = os.getenv("VERIFYTOKEN")


def get_telegram_bot_url():
    """Return a public Telegram link only when it is a valid HTTPS t.me URL."""
    candidate = os.getenv("TELEGRAM_BOT_URL", "").strip()
    try:
        parsed = urlsplit(candidate)
        valid_port = parsed.port in (None, 443)
    except ValueError:
        return None

    if (
        parsed.scheme == "https"
        and parsed.hostname in {"t.me", "telegram.me"}
        and parsed.path.strip("/")
        and not parsed.username
        and not parsed.password
        and valid_port
    ):
        return candidate
    return None


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", telegram_bot_url=get_telegram_bot_url())


@app.route("/healthz", methods=["GET"])
def healthz():
    return jsonify(status="ok"), 200


# Verify the webhook with Meta.
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if VERIFYTOKEN and mode == "subscribe" and token == VERIFYTOKEN:
        app.logger.info("Meta webhook verification succeeded.")
        return challenge or "", 200
    return "Verification token mismatch", 403


# Receive messages sent to the Meta Page.
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return "Invalid JSON", 400

    if data.get("object") != "page":
        return "Not Found", 404

    for entry in data.get("entry", []):
        if not isinstance(entry, dict):
            continue
        for messaging_event in entry.get("messaging", []):
            if not isinstance(messaging_event, dict):
                continue
            message = messaging_event.get("message")
            if not isinstance(message, dict) or message.get("is_echo"):
                continue

            sender_id = messaging_event.get("sender", {}).get("id")
            if not sender_id:
                continue

            user_text = message.get("text", "")
            reply_text = f"Cooler Bot បានទទួលសារ៖ {user_text}"
            send_message(sender_id, reply_text)

    return "EVENT_RECEIVED", 200


def send_message(recipient_id, message_text):
    if not PAGEACCESSTOKEN:
        app.logger.error("Cannot send a Meta message: PAGEACCESSTOKEN is not configured.")
        return

    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"access_token": PAGEACCESSTOKEN}
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }

    response = requests.post(
        url,
        params=params,
        headers=headers,
        json=payload,
        timeout=10,
    )
    response.raise_for_status()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
