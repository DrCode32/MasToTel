import requests
import json
from telegram.ext import Updater, CommandHandler, MessageHandler
from telegram.utils.request import Request

mastodon_instance = 'https://mastodon.example.com'
mastodon_access_token = 'your_mastodon_access_token'
accounts_to_track = ['account1', 'account2']

telegram_token = 'your_telegram_bot_token'
telegram_channel_id = '@your_telegram_channel_id'

def get_mastodon_posts():
    posts = []
    for account in accounts_to_track:
        url = f'{mastodon_instance}/api/v1/accounts/{account}/statuses'
        headers = {'Authorization': f'Bearer {mastodon_access_token}'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            posts.extend(response.json())
    return posts

def send_telegram_message(post):
    text = f'{post["content"]}\nSender: [{post["account"]["username"]}]({mastodon_instance}/@{post["account"]["username"]})'
    if 'media_attachments' in post:
        media_url = post['media_attachments'][0]['url']
        requests.post(f'https://api.telegram.org/bot{telegram_token}/sendPhoto', 
                      data={'chat_id': telegram_channel_id, 'photo': media_url, 'caption': text})
    else:
        requests.post(f'https://api.telegram.org/bot{telegram_token}/sendMessage', 
                      data={'chat_id': telegram_channel_id, 'text': text})

def main():
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', lambda update, context: context.bot.send_message(chat_id=update.effective_chat.id, text='Mastodon to Telegram bot started')))
    dp.add_handler(MessageHandler(None, lambda update, context: None))
    updater.start_polling()
    while True:
        posts = get_mastodon_posts()
        for post in posts:
            send_telegram_message(post)

if __name__ == '__main__':
    main()
