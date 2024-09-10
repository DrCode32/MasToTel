import os
import mastodon
import telegram
from telegram.ext import Application, CommandHandler
import html2text

mastodon_instance = 'https://mastodon.example.com'
mastodon_access_token = 'your_access_token_here'
telegram_token = 'your_telegram_token_here'
telegram_channel_id = 'your_telegram_channel_id_here'

# Mastodon client setup
m = mastodon.Mastodon(
    access_token=mastodon_access_token,
    api_base_url=mastodon_instance
)

# Telegram bot setup
bot = telegram.Bot(token=telegram_token)

# HTML to text converter
h = html2text.HTML2Text()
h.ignore_links = False

# Send message function
async def send_message(text, media=None):
    try:
        if media:
            await bot.send_photo(chat_id=telegram_channel_id, photo=media, caption=text)
        else:
            await bot.send_message(chat_id=telegram_channel_id, text=text)
    except Exception as e:
        print(f"Error sending message: {e}")

# Fetch and process Mastodon statuses
async def process_mastodon_statuses():
    try:
        statuses = m.timeline(timeline='home', limit=100)
        for status in statuses:
            content = h.handle(status['content'])
            sender = status['account']['username']
            sender_url = f"https://{mastodon_instance}/@{sender}"

            # Handle media attachments if available
            media_url = None
            for attachment in status['media_attachments']:
                if attachment['type'] == 'image':
                    media_url = attachment['url']

            text = f"{content}\n{sender} - {sender_url}"
            await send_message(text, media_url)
    except Exception as e:
        print(f"Error fetching Mastodon statuses: {e}")

# Start command for Telegram bot
async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Mastodon bot started!")

# Main function to initialize Telegram bot
async def main():
    app = Application.builder().token(telegram_token).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start))

    # Start bot
    await app.start_polling()
    await process_mastodon_statuses()
    await app.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
