import os
from mastodon import Mastodon
import requests
from html2text import html2text
import time

# Mastodon API setup
mastodon = Mastodon(
    access_token=os.environ.get('MASTODON_ACCESS_TOKEN'),
    api_base_url=os.environ.get('MASTODON_INSTANCE')
)

# Telegram Bot API setup
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def send_telegram_message(text, parse_mode="HTML"):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    response = requests.post(url, json=payload)
    return response.json()

def send_telegram_media(file_url, caption, media_type):
    url = f"{TELEGRAM_API_URL}/send{media_type.capitalize()}"
    payload = {
        "chat_id": TELEGRAM_CHANNEL_ID,
        "caption": caption,
        "parse_mode": "HTML"
    }
    files = {media_type: requests.get(file_url).content}
    response = requests.post(url, data=payload, files=files)
    return response.json()

def process_status(status):
    content = html2text(status['content'])
    author = status['account']['acct']
    post_url = status['url']
    message = f"{content}\n<a href='{post_url}'>{author}</a>"

    if status['media_attachments']:
        for media in status['media_attachments']:
            media_url = media['url']
            media_type = media['type']
            if media_type in ['image', 'video']:
                send_telegram_media(media_url, message, media_type)
            else:
                send_telegram_message(f"{message}\n\nMedia URL: {media_url}")
    else:
        send_telegram_message(message)

def main():
    last_id = None
    while True:
        try:
            timeline = mastodon.account_statuses(mastodon.me(), since_id=last_id)
            for status in reversed(timeline):
                process_status(status)
                last_id = status['id']

            # Process replies
            notifications = mastodon.notifications(since_id=last_id)
            for notif in reversed(notifications):
                if notif['type'] == 'mention':
                    process_status(notif['status'])
                    last_id = notif['id']

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
