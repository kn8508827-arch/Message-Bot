# Cooler Bot website and Meta webhook

This Railway service serves a small public landing page for Cooler Bot and retains the existing Meta Messenger webhook at `/webhook`.

## Public page

The landing page at `/` describes the verified bot features in Khmer and English: AI chat and voice, image analysis and Photo Studio, fuel and EV charging location search, and opt-in Daily Care messages. AI, voice, and image features depend on their services being configured and available.

The Telegram call-to-action appears only when the optional `TELEGRAM_BOT_URL` variable contains an HTTPS link on `t.me` or `telegram.me`, such as `https://t.me/your_bot_name`. This must be a public bot link; do not put bot tokens or API keys in it.

## Existing Meta webhook

The webhook continues to use the Railway variables `PAGEACCESSTOKEN` and `VERIFYTOKEN`. Keep their secret values in Railway Variables. The health check is available at `/healthz`.

The Telegram bot runs separately and uses long polling. This website does not connect to its SQLite database or expose private bot data.
