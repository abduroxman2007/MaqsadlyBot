# Always return the static, human-generated invite link

STATIC_INVITE_LINK = 'https://t.me/+LDSL7ArQ7w8yOTJi'

def get_static_invite_link():
    print('[INVITE] Returning static invite link.')
    return STATIC_INVITE_LINK

from telegram import Bot
from config import PRIVATE_GROUP_ID

async def generate_unique_invite_link(bot: Bot):
    print('[INVITE] Generating unique invite link...')
    invite_link = await bot.create_chat_invite_link(
        chat_id=PRIVATE_GROUP_ID,
        member_limit=1,
        name="Maqsadly Marathon Single-Use Link"
    )
    print(f'[INVITE] Generated invite link: {invite_link.invite_link}')
    return invite_link.invite_link

async def revoke_invite_link(bot: Bot, invite_link_id: str):
    print(f'[INVITE] Revoking invite link with ID: {invite_link_id}')
    await bot.revoke_chat_invite_link(
        chat_id=PRIVATE_GROUP_ID,
        invite_link=invite_link_id
    )
    print('[INVITE] Invite link revoked.') 