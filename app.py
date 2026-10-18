import os
import requests
from flask import Flask, request

app = Flask(name)

# ទាញយក Token ពី Variables លើ Railway
PAGEACCESSTOKEN = os.getenv("PAGEACCESSTOKEN")
VERIFYTOKEN = os.getenv("VERIFYTOKEN")


# ១. ផ្ទៀងផ្ទាត់ Webhook ជាមួយ Meta
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verifytoken")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFYTOKEN:
        print("WEBHOOKVERIFIED")
        return challenge, 200
    return "Verification token mismatch", 403


# ២. ទទួលសារពេលគេឆាតមក Page
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.getjson()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messagingevent in entry.get("messaging", []):
                # ពិនិត្យមើលថាតើជាសារធម្មតាអត់
                if messagingevent.get("message") and not messagingevent.get(
                    "message"
                ).get("isecho"):
                    senderid = messagingevent["sender"]["id"]
                    usertext = messagingevent["message"].get("text", "")

                    # ឆ្លើយតបទៅវិញ (Bot ឆ្លើយត្រាប់តាម ឬប៉ាអាចប្តូរតាមចិត្ត)
                    replytext = f"Cooler Bot បានទទួលសារ៖ {usertext}"
                    sendmessage(senderid, replytext)

        return "EVENTRECEIVED", 200
    return "Not Found", 404


# មុខងារផ្ញើសារត្រឡប់ទៅ User វិញ
def sendmessage(recipientid, messagetext):
    url = "https://graph.facebook.com/v19.0/me/messages"
    params = {"accesstoken": PAGEACCESSTOKEN}
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": recipientid},
        "message": {"text": messagetext},
    }

    requests.post(url, params=params, headers=headers, json=payload)


if name == "main":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
