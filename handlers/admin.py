from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from data.db import get_all_users
import pandas as pd
import io
from config import ADMIN_IDS, CHANNEL_IDS
import asyncio

ADMIN_ID = 440036522
BROADCAST = range(1)

# States
BROADCAST_TEXT, BROADCAST_CONFIRM = range(2)

def get_admin_keyboard():
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton('📊 Statistics'), KeyboardButton('📥 Export Users (Excel)')],
            [KeyboardButton('🤖 Bot Admin Channels'), KeyboardButton('📢 Send Message to All')],
        ],
        resize_keyboard=True
    )

async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('⛔️ You are not authorized to use this command.')
        return
    keyboard = [
        [InlineKeyboardButton('📊 Statistics', callback_data='admin_stats')],
        [InlineKeyboardButton('📥 Export Users (Excel)', callback_data='admin_export')],
        [InlineKeyboardButton('🤖 Bot Admin Channels', callback_data='admin_channels')],
    ]
    await update.message.reply_text('Admin Panel:', reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.answer('⛔️ Not authorized.', show_alert=True)
        return
    await admin_stats_from_message(update, context, query=query)

async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('⛔️ You are not authorized to use this command.')
        return
    await admin_stats_from_message(update, context)

async def admin_stats_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None, reply_markup=None):
    if query:
        send_func = query.edit_message_text
    else:
        send_func = update.message.reply_text
    users = await get_all_users()
    total = len(users)
    eligible = sum(1 for u in users if u['eligible_at'])
    approved = sum(1 for u in users if u['approved_at'])
    msg = (
        f'📊 <b>Statistics</b>\n'
        f'Total users: <b>{total}</b>\n'
        f'Eligible users: <b>{eligible}</b>\n'
        f'Approved users: <b>{approved}</b>\n'
    )
    await send_func(msg, parse_mode='HTML', reply_markup=reply_markup)

async def admin_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.answer('⛔️ Not authorized.', show_alert=True)
        return
    await admin_export_from_message(update, context, query=query)

async def admin_export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('⛔️ You are not authorized to use this command.')
        return
    await admin_export_from_message(update, context)

async def admin_export_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None, reply_markup=None):
    if query:
        send_func = query.edit_message_text
        chat_id = query.from_user.id
    else:
        send_func = update.message.reply_text
        chat_id = update.effective_user.id
    users = await get_all_users()
    if not users:
        await send_func('User database is empty, nothing to export.', reply_markup=reply_markup)
        return
    df = pd.DataFrame(users)
    output = io.BytesIO()
    df.to_excel(output, index=False)
    output.seek(0)
    await context.bot.send_document(
        chat_id=chat_id,
        document=output,
        filename='users.xlsx',
        caption='User database export'
    )
    await send_func('Exported!', reply_markup=reply_markup)

async def admin_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    if user_id not in ADMIN_IDS:
        await query.answer('⛔️ Not authorized.', show_alert=True)
        return
    await query.answer()
    admin_in = []
    not_admin_in = []
    for channel_id, name in CHANNEL_IDS.items():
        try:
            chat_member = await context.bot.get_chat_member(channel_id, context.bot.id)
            if chat_member.status in ['administrator', 'creator']:
                admin_in.append(name)
            else:
                not_admin_in.append(name)
        except Exception as e:
            not_admin_in.append(f"{name} (error: {e})")
    msg = "🤖 <b>Bot Admin Status in Channels:</b>\n\n"
    if admin_in:
        msg += "✅ Admin in:\n" + "\n".join(f"• {c}" for c in admin_in) + "\n\n"
    if not_admin_in:
        msg += "❌ Not admin in:\n" + "\n".join(f"• {c}" for c in not_admin_in)
    await query.edit_message_text(msg, parse_mode='HTML')

async def admin_channels_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text('⛔️ You are not authorized to use this command.')
        return
    admin_in = []
    not_admin_in = []
    for channel_id, name in CHANNEL_IDS.items():
        try:
            chat_member = await context.bot.get_chat_member(channel_id, context.bot.id)
            if chat_member.status in ['administrator', 'creator']:
                admin_in.append(name)
            else:
                not_admin_in.append(name)
        except Exception as e:
            not_admin_in.append(f"{name} (error: {e})")
    msg = "🤖 <b>Bot Admin Status in Channels:</b>\n\n"
    if admin_in:
        msg += "✅ Admin in:\n" + "\n".join(f"• {c}" for c in admin_in) + "\n\n"
    if not_admin_in:
        msg += "❌ Not admin in:\n" + "\n".join(f"• {c}" for c in not_admin_in)
    await update.message.reply_text(msg, parse_mode='HTML')

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text('⛔️ You are not authorized to use this command.')
        return ConversationHandler.END
    await update.message.reply_text("✉️ Send the message to broadcast now:")
    return BROADCAST_TEXT

async def broadcast_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Store the full message object and message_id for later use
    context.user_data['broadcast_message'] = update.message
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data='bconfirm')],
        [InlineKeyboardButton("❌ Cancel", callback_data='bcancel')],
    ])
    # Show a preview depending on the message type
    preview_text = "Here's the message you typed. It will be sent as-is to all users."
    await update.message.reply_text(preview_text, reply_markup=keyboard)
    return BROADCAST_CONFIRM

async def broadcast_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'bconfirm':
        orig_message = context.user_data.get('broadcast_message')
        users = await get_all_users()
        sent = failed = 0
        for u in users:
            try:
                # If the message is a reply, broadcast the replied-to message
                msg_to_send = orig_message.reply_to_message if orig_message.reply_to_message else orig_message
                # Send according to message type
                if msg_to_send.text and not msg_to_send.photo and not msg_to_send.document and not msg_to_send.video:
                    await context.bot.send_message(chat_id=int(u['user_id']), text=msg_to_send.text)
                elif msg_to_send.photo:
                    await context.bot.send_photo(chat_id=int(u['user_id']), photo=msg_to_send.photo[-1].file_id, caption=msg_to_send.caption or "")
                elif msg_to_send.document:
                    await context.bot.send_document(chat_id=int(u['user_id']), document=msg_to_send.document.file_id, caption=msg_to_send.caption or "")
                elif msg_to_send.video:
                    await context.bot.send_video(chat_id=int(u['user_id']), video=msg_to_send.video.file_id, caption=msg_to_send.caption or "")
                elif msg_to_send.audio:
                    await context.bot.send_audio(chat_id=int(u['user_id']), audio=msg_to_send.audio.file_id, caption=msg_to_send.caption or "")
                elif msg_to_send.voice:
                    await context.bot.send_voice(chat_id=int(u['user_id']), voice=msg_to_send.voice.file_id, caption=msg_to_send.caption or "")
                elif msg_to_send.sticker:
                    await context.bot.send_sticker(chat_id=int(u['user_id']), sticker=msg_to_send.sticker.file_id)
                elif msg_to_send.animation:
                    await context.bot.send_animation(chat_id=int(u['user_id']), animation=msg_to_send.animation.file_id, caption=msg_to_send.caption or "")
                else:
                    # fallback: try to copy the message
                    await context.bot.copy_message(chat_id=int(u['user_id']), from_chat_id=orig_message.chat_id, message_id=msg_to_send.message_id)
                sent += 1
                await asyncio.sleep(0.05)
            except Exception as e:
                failed += 1
        await query.edit_message_text(f"✅ Sent to {sent}, failed {failed}.")
    else:
        await query.edit_message_text("❌ Broadcast cancelled.")
    context.user_data.clear()
    return ConversationHandler.END

broadcast_conv = ConversationHandler(
    entry_points=[CommandHandler('broadcast', broadcast_start)],
    states={
        BROADCAST_TEXT: [MessageHandler(filters.ALL & ~filters.COMMAND, broadcast_receive)],
        BROADCAST_CONFIRM: [CallbackQueryHandler(broadcast_confirm, pattern='^b')]
    },
    fallbacks=[]
)

admin_handler = CommandHandler('admin', admin_menu)
admin_stats_handler = CallbackQueryHandler(admin_stats, pattern='^admin_stats$')
admin_stats_command_handler = CommandHandler('statistics', admin_stats_command)
admin_export_handler = CallbackQueryHandler(admin_export, pattern='^admin_export$')
admin_export_command_handler = CommandHandler('export', admin_export_command)
admin_channels_handler = CallbackQueryHandler(admin_channels, pattern='^admin_channels$')
admin_channels_command_handler = CommandHandler('channels', admin_channels_command) 