import os
from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS
from UCHIHA import app
from UCHIHA.utils.database import get_loop
from UCHIHA.utils.stream.filters import command
from UCHIHA.utils.decorators import language
from UCHIHA.utils.stream.stream import stream
from UCHIHA.utils.stream.ytstream import yt_stream
from UCHIHA.utils.inline.play import stream_markup

@app.on_message(
    command(["play", "vplay", "cplay"]) & filters.group & ~BANNED_USERS
)
@language
async def play_handler(client, message: Message, _):
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("Please provide a song name or reply to a media.")

    if message.reply_to_message and message.reply_to_message.audio:
        link = message.reply_to_message.audio.file_id
        title = message.reply_to_message.audio.title or "Telegram Audio"
        performer = message.reply_to_message.audio.performer or "Unknown"
        duration = message.reply_to_message.audio.duration
        return await stream(
            client,
            message,
            title=title,
            videoid=link,
            user_id=message.from_user.id,
            duration=duration,
            streamtype="telegram",
            playmode="Audio",
            query=None,
        )

    query = (
        message.text.split(None, 1)[1]
        if len(message.command) >= 2
        else None
    )
    if not query:
        return await message.reply_text("What should I play?")

    await yt_stream(client, message, query)
