from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, ContextTypes
from utils.messages import GREETING_MESSAGE, SUBSCRIPTION_MESSAGE
from utils.subscription import get_subscription_links
from data.db import add_or_update_user, get_user
from config import ADMIN_IDS

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    print(f'[START] /start from user {user.id} ({user.username})')
    await add_or_update_user(user.id, user.username, user.first_name, user.last_name)
    print(f'ADMIN_IDS: {ADMIN_IDS}, user.id: {user.id}')
    if int(user.id) in [int(aid) for aid in ADMIN_IDS]:
        # Admin custom greeting and reply keyboard
        admin_msg = (
            '👋 Hello, admin! Here are all the available functions for you:'
            '\n\n'
            '• /statistics — View statistics\n'
            '• /export — Export users (Excel)\n'
            '• /channels — See which channels the bot is admin in\n'
            '• /broadcast — Send a message to all users\n'
        )
        keyboard = [
            [KeyboardButton('/statistics'), KeyboardButton('/export')],
            [KeyboardButton('/channels'), KeyboardButton('/broadcast')],
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(admin_msg, reply_markup=reply_markup)
        return
    else:
        user_row = await get_user(user.id)
        if user_row and user_row[5]:  # eligible_at
            await update.message.reply_text(
                "✅ You are already registered or eligible to join the channel!"
            )
        elif user_row and user_row[6]:  # approved_at
            await update.message.reply_text("✅ You have already joined the channel!")
        else:
            await update.message.reply_text(GREETING_MESSAGE.format(name=user.first_name))
            folder_text, folder_url = get_subscription_links()
            keyboard = [[InlineKeyboardButton("Add Folder", url=folder_url)]]
            keyboard.append([InlineKeyboardButton('Check', callback_data='check_subscription')])
            await update.message.reply_text(
                f"Add this folder to your Telegram to subscribe to all required channels. (12 channels)\n\nAfter adding, press 'Check' to verify your subscription.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

start_handler = CommandHandler('start', start) 