from telegram import Update
from telegram.ext import ChatJoinRequestHandler, ContextTypes
from config import PRIVATE_GROUP_ID
from data.db import is_eligible, set_approved
# from utils.invite import generate_unique_invite_link

# In production, you should check if the user has passed the subscription check
async def handle_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    join_request = update.chat_join_request
    user_id = join_request.from_user.id
    print(f'[JOIN REQUEST] Received join request from user {user_id} for chat {join_request.chat.id}')
    if join_request.chat.id == PRIVATE_GROUP_ID:
        if await is_eligible(user_id):
            print(f'[JOIN REQUEST] User {user_id} is eligible. Approving join request.')
            await join_request.approve()
            await set_approved(user_id)
            # Generate a unique invite link
            # invite_link = await generate_unique_invite_link(context.bot)
            # Send the link to the user via private message
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text='🎉 You were accepted to the channel, congrats! 🎉',
                    reply_markup=None
                )
            except Exception as e:
                print(f'[JOIN REQUEST] Failed to send invite link to user {user_id}: {e}')
        else:
            print(f'[JOIN REQUEST] User {user_id} is NOT eligible. Ignoring join request.')
    else:
        print(f'[JOIN REQUEST] Join request is for unknown chat {join_request.chat.id}. Ignoring.')

join_request_handler = ChatJoinRequestHandler(handle_join_request) 