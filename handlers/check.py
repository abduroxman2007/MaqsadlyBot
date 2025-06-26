from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from utils.subscription import check_user_subscriptions, get_subscription_links
# from utils.invite import get_static_invite_link
from config import CHANNEL_IDS  # Now a dict: {channel_id: "Channel Name"}
from data.db import set_eligible
from telegram.error import BadRequest

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    print(f'[CHECK] User {user_id} pressed Check button.')
    try:
        await query.answer()
    except BadRequest as e:
        if "Query is too old" in str(e) or "query id is invalid" in str(e):
            return  # Ignore and do not crash
        else:
            raise
    unsubscribed = await check_user_subscriptions(context.bot, user_id)
    print(f'[CHECK] Unsubscribed channels for user {user_id}: {unsubscribed}')
    if not unsubscribed:
        print(f'[CHECK] User {user_id} is subscribed to all channels. Instructing to use join request link...')
        await set_eligible(user_id)
        msg = (
            '✅ You have subscribed to all channels!\n'
            'Now click the button below to request access to the special channel. Your request will be approved by an admin soon.'
        )
        join_request_link = 'https://t.me/+LDSL7ArQ7w8yOTJi'  # Replace with your actual join request link
        keyboard = [[InlineKeyboardButton('Request Access to Private Channel', url=join_request_link)]]
        await query.edit_message_text(
            msg,
            parse_mode='HTML',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        msg = '❌ You have not yet subscribed to the following channels (11 total):\n\n'
        for channel_id in unsubscribed:
            name = CHANNEL_IDS.get(channel_id, 'Unknown channel')
            msg += f'• {name}\n'
        folder_text, folder_url = get_subscription_links()
        msg += f"\n{folder_text}\n"
        keyboard = [[InlineKeyboardButton('Add Folder', url=folder_url)], [InlineKeyboardButton('Check', callback_data='check_subscription')]]
        try:
            await query.edit_message_text(
                msg,
                parse_mode='HTML',
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except BadRequest as e:
            if "Message is not modified" in str(e):
                pass
            else:
                raise

check_handler = CallbackQueryHandler(check_subscription, pattern='^check_subscription$') 