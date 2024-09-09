import os
import mastodon
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler


mastodon_instance = 'https://mastodon.example.com'
mastodon_access_token = ' your_access_token_here'


telegram_token = 'your_telegram_token_here'
telegram_channel_id = 'your_telegram_channel_id_here'


m = mastodon.Mastodon(
    access_token=mastodon_access_token,
    api_base_url=mastodon_instance
)


bot = telegram.Bot(token=telegram_token)


def send_message(text, media=None):
    if media:
        bot.send_photo(chat_id=telegram_channel_id, photo=media, caption=text)
    else:
        bot.send_message(chat_id=telegram_channel_id, text=text)


statuses = m.timeline(timeline='home', limit=100)


for status in statuses:

    content = status['content']
    sender = status['account']['username']
    sender_url = f'https://{mastodon_instance}/@{sender}'

    
    media_url = None
    for attachment in status['media_attachments']:
        if attachment['type'] == 'image':
            media_url = attachment['url']


    text = f'{content}\n{sender} - {sender_url}'
    send_message(text, media_url)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Mastodon bot started!')

def main():
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
