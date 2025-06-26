from telegram import Bot
from config import CHANNEL_IDS

async def check_user_subscriptions(bot: Bot, user_id: int):
    unsubscribed = []
    print(f'[SUB CHECK] Checking subscriptions for user {user_id}...')
    for channel_id in CHANNEL_IDS:
        try:
            print(f'[SUB CHECK] Checking channel {channel_id} ({CHANNEL_IDS[channel_id]}) for user {user_id}...')
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            print(f'[SUB CHECK] Status for user {user_id} in channel {channel_id}: {member.status}')
            if member.status not in ['member', 'administrator', 'creator']:
                print(f'[SUB CHECK] User {user_id} is NOT subscribed to {channel_id}')
                unsubscribed.append(channel_id)
        except Exception as e:
            print(f'[SUB CHECK] Exception while checking channel {channel_id} for user {user_id}: {e}')
            unsubscribed.append(channel_id)
    print(f'[SUB CHECK] Unsubscribed channels for user {user_id}: {unsubscribed}')
    return unsubscribed

def get_subscription_links():
    # Return a single folder link for all channels
    folder_text = "Add this folder to your Telegram to subscribe to all required channels."
    folder_url = "https://t.me/addlist/LJ_cpy1x5CM5YzZi"
    return folder_text, folder_url 