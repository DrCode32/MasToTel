import os
import mastodon
import telegram
from telegram.ext import Application, CommandHandler
import html2text

mastodon_instance = 'https://mastodon.example.com'
mastodon_access_token = 'your_access_token_here'
telegram_token = 'your_telegram_token_here'
telegram_channel_id = 'your_telegram_channel_id_here'


m = mastodon.Mastodon(
    access_token=mastodon_access_token,
    api_base_url=mastodon_instance
)


bot = telegram.Bot(token=telegram_token)


h = html2text.HTML2Text()
h.ignore_links = False


async def send_message(text, media=None):
    try:
        if media:
            await bot.send_photo(chat_id=telegram_channel_id, photo=media, caption=text)
        else:
            await bot.send_message(chat_id=telegram_channel_id, text=text)
    except Exception as e:
        print(f"Error sending message: {e}")


async def process_mastodon_statuses():
    try:
        statuses = m.timeline(timeline='home', limit=100)
        for status in statuses:
            content = h.handle(status['content'])
            sender = status['account']['username']
            sender_url = f"https://{mastodon_instance}/@{sender}"

            
            media_url = None
            for attachment in status['media_attachments']:
                if attachment['type'] == 'image':
                    media_url = attachment['url']

            text = f"{content}\n{sender} - {sender_url}"
            await send_message(text, media_url)
    except Exception as e:
        print(f"Error fetching Mastodon statuses: {e}")


async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Mastodon bot started!")


async def main():
    app = Application.builder().token(telegram_token).build()


    app.add_handler(CommandHandler('start', start))

    
    await app.start_polling()
    await process_mastodon_statuses()
    await app.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
