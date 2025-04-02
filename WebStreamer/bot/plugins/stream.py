import logging
from telethon import Button, errors
from telethon.events import NewMessage
from telethon.extensions import html
from WebStreamer.bot import StreamBot
from WebStreamer.utils.file_properties import get_file_info, pack_file, get_short_hash
from WebStreamer.vars import Var

# Enable logging
logging.basicConfig(level=logging.INFO)

@StreamBot.on(NewMessage(func=lambda e: True if e.message.file and e.is_private else False))
async def media_receive_handler(event: NewMessage.Event):
    user = await event.get_sender()

    # Check if the user is allowed to use the bot
    if Var.ALLOWED_USERS and not ((str(user.id) in Var.ALLOWED_USERS) or (user.username in Var.ALLOWED_USERS)):
        return await event.message.reply(
            message="❌ You are not authorized to use this bot.",
            link_preview=False,
            parse_mode=html
        )

    try:
        # Forward the received file to the BIN_CHANNEL
        log_msg = await event.message.forward_to(Var.BIN_CHANNEL)
        file_info = get_file_info(log_msg)

        # Generate file hash and stream link
        full_hash = pack_file(
            file_info.file_name,
            file_info.file_size,
            file_info.mime_type,
            file_info.id
        )
        file_hash = get_short_hash(full_hash)
        stream_link = f"{Var.URL}stream/{log_msg.id}?hash={file_hash}"

        # Construct the message output
        reply_text = f"""
𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱! ✅

📂 Fɪʟᴇ ɴᴀᴍᴇ : `{file_info.file_name}`

📥 Download : ({stream_link})
"""
        # Send response with the stream button
        await event.message.reply(
            message=reply_text,
            link_preview=False,
            buttons=[
                [Button.url("📥 Download", url=stream_link)]
            ],
            parse_mode=html
        )

    except errors.FloodWaitError as e:
        logging.error(f"FloodWaitError: {e}")
        await event.message.reply("⚠️ Slow down! Telegram is limiting requests. Please wait.")
