# Copyright (C) 2024 by Badhacker98@Github, < https://github.com/Badhacker98 >.
# Owner https://t.me/ll_BAD_MUNDA_ll

import re
from math import ceil
from typing import Union

from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from config import BANNED_USERS, START_IMG_URL
from strings import get_command, get_string
from UCHIHA import HELPABLE, app
from UCHIHA.utils.database import get_lang, is_commanddelete_on
from UCHIHA.utils.decorators.language import LanguageStart
from UCHIHA.utils.inline.help import private_help_panel

### Command
HELP_COMMAND = get_command("HELP_COMMAND")

COLUMN_SIZE = 4  # number of  button height
NUM_COLUMNS = 3  # number of button width

donate = "https://envs.sh/Sgb.jpg"


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n, module_dict, prefix, chat=None, close: bool = False):
    if not chat:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{})".format(
                        prefix, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )
    else:
        modules = sorted(
            [
                EqInlineKeyboardButton(
                    x.__MODULE__,
                    callback_data="{}_module({},{},{})".format(
                        prefix, chat, x.__MODULE__.lower(), page_n
                    ),
                )
                for x in module_dict.values()
            ]
        )

    pairs = [modules[i : i + NUM_COLUMNS] for i in range(0, len(modules), NUM_COLUMNS)]

    max_num_pages = ceil(len(pairs) / COLUMN_SIZE) if len(pairs) > 0 else 1
    modulo_page = page_n % max_num_pages

    if len(pairs) > COLUMN_SIZE:
        pairs = pairs[modulo_page * COLUMN_SIZE : COLUMN_SIZE * (modulo_page + 1)] + [
            (
                EqInlineKeyboardButton(
                    "❮",
                    callback_data="{}_prev({})".format(
                        prefix,
                        modulo_page - 1 if modulo_page > 0 else max_num_pages - 1,
                    ),
                ),
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
                EqInlineKeyboardButton(
                    "❯",
                    callback_data="{}_next({})".format(prefix, modulo_page + 1),
                ),
            )
        ]
    else:
        pairs.append(
            [
                EqInlineKeyboardButton(
                    "ᴄʟᴏsᴇ" if close else "Bᴀᴄᴋ",
                    callback_data="close" if close else "feature",
                ),
            ]
        )

    return pairs


@app.on_message(filters.command(HELP_COMMAND) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass

        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await update.edit_message_text(_["help_1"], reply_markup=keyboard)
    else:
        chat_id = update.chat.id
        if await is_commanddelete_on(update.chat.id):
            try:
                await update.delete()
            except:
                pass
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = InlineKeyboardMarkup(
            paginate_modules(0, HELPABLE, "help", close=True)
        )
        if START_IMG_URL:

            await update.reply_photo(
                photo=START_IMG_URL,
                caption=_["help_1"],
                reply_markup=keyboard,
            )

        else:

            await update.reply_text(
                text=_["help_1"],
                reply_markup=keyboard,
            )


@app.on_message(filters.command(HELP_COMMAND) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return keyboard


@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(client, query):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?),(.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back\((\d+)\)", query.data)
    create_match = re.match(r"help_create", query.data)
    language = await get_lang(query.message.chat.id)
    _ = get_string(language)
    top_text = _["help_1"]

    if mod_match:
        module = mod_match.group(1)
        prev_page_num = int(mod_match.group(2))
        text = (
            f"<b><u>Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ {HELPABLE[module].__MODULE__}:</u></b>\n"
            + HELPABLE[module].__HELP__
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="↪️ ʙᴀᴄᴋ", callback_data=f"help_back({prev_page_num})"
                    ),
                    InlineKeyboardButton(text="🔄 ᴄʟᴏsᴇ", callback_data="close"),
                ],
            ]
        )

        await query.message.edit(
            text=text,
            reply_markup=key,
            disable_web_page_preview=True,
        )

    elif home_match:
        await app.send_message(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=InlineKeyboardMarkup(out),
        )
        await query.message.delete()

    elif prev_match:
        curr_page = int(prev_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(curr_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(next_page, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif back_match:
        prev_page_num = int(back_match.group(1))
        await query.message.edit(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(
                paginate_modules(prev_page_num, HELPABLE, "help")
            ),
            disable_web_page_preview=True,
        )

    elif create_match:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))

        await query.message.edit(
            text=top_text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    await client.answer_callback_query(query.id)


# ===================================

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import BANNED_USERS
from strings import helpers
from BADMUSIC import app
from BADMUSIC.utils.decorators.language import languageCB


@app.on_callback_query(filters.regex("music_callback") & ~BANNED_USERS)
@languageCB
async def music_helper_cb(client, CallbackQuery, _):

    callback_data = CallbackQuery.data.strip()

    cb = callback_data.split(None, 1)[1]

    keyboard = back_to_music(_)

    if cb == "hb1":

        await CallbackQuery.edit_message_text(helpers.HELP_1, reply_markup=keyboard)

    elif cb == "hb2":

        await CallbackQuery.edit_message_text(helpers.HELP_2, reply_markup=keyboard)

    elif cb == "hb3":

        await CallbackQuery.edit_message_text(helpers.HELP_3, reply_markup=keyboard)

    elif cb == "hb4":

        await CallbackQuery.edit_message_text(helpers.HELP_4, reply_markup=keyboard)

    elif cb == "hb5":

        await CallbackQuery.edit_message_text(helpers.HELP_5, reply_markup=keyboard)

    elif cb == "hb6":

        await CallbackQuery.edit_message_text(helpers.HELP_6, reply_markup=keyboard)

    elif cb == "hb7":

        await CallbackQuery.edit_message_text(helpers.HELP_7, reply_markup=keyboard)

    elif cb == "hb8":

        await CallbackQuery.edit_message_text(helpers.HELP_8, reply_markup=keyboard)

    elif cb == "hb9":

        await CallbackQuery.edit_message_text(helpers.HELP_9, reply_markup=keyboard)

    elif cb == "hb10":

        await CallbackQuery.edit_message_text(helpers.HELP_10, reply_markup=keyboard)

    elif cb == "hb11":

        await CallbackQuery.edit_message_text(helpers.HELP_11, reply_markup=keyboard)

    elif cb == "hb12":

        await CallbackQuery.edit_message_text(helpers.HELP_12, reply_markup=keyboard)

    elif cb == "hb13":

        await CallbackQuery.edit_message_text(helpers.HELP_13, reply_markup=keyboard)

    elif cb == "hb14":

        await CallbackQuery.edit_message_text(helpers.HELP_14, reply_markup=keyboard)

    elif cb == "hb15":

        await CallbackQuery.edit_message_text(helpers.HELP_15, reply_markup=keyboard)


@app.on_callback_query(filters.regex("developer"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="👨‍💻 ᴄ❍ᴅᴇꝛ 👨‍💻", user_id=config.OWNER_ID[0]),
            InlineKeyboardButton(
                text="📍sᴜᴅᴏᴇʀs📍", url=f"https://t.me/{app.username}?start=sudo"
            ),
        ],
        [
            InlineKeyboardButton(text="🔗 TELEGRAM 🔗", url=f"https://t.me/uchiha_owner"),
            InlineKeyboardButton(text="🎊 SUPPORT 🎊", url=f"https://t.me/SNOWY_HOMETOWN"),
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="about")
        ],  # Use a default label for the back button
    ]
    await callback_query.message.edit_text(
        "<blockquote>ʀᴇᴛᴜʀɴɪɴɢ ᴛᴏ ᴀʙᴏᴜᴛ ᴏᴘᴛɪᴏɴꜱ...<blockquote>", reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("feature"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="💫 ᴀᴅᴅ ᴍᴇ ᴍᴏʀᴇ ❤️",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🎧 ᴍᴜsɪᴄ 🎧", callback_data="music"),
            InlineKeyboardButton(text="🤖 ᴍᴀɴᴇɢᴇᴍᴇɴᴛ 🤖", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        f"<blockquote><b>**Wᴇʟᴄᴏᴍᴇ ᴛᴏ** {app.mention}\n\n**Exᴘʟᴏʀᴇ ᴀ ᴡɪᴅᴇ ʀᴀɴɢᴇ ᴏғ ғᴇᴀᴛᴜʀᴇs ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ᴇɴʜᴀɴᴄᴇ ʏᴏᴜʀ ᴍᴜsɪᴄ ᴇxᴘᴇʀɪᴇɴᴄᴇ. Tᴀᴘ KIDNAP ME IN YOUR NEW GROUP OR CHANNEL ᴛᴏ ɪɴᴠɪᴛᴇ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ᴏᴡɴ ɢʀᴏᴜᴘ ᴏʀ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴇɴɪᴏʏ sᴇᴀᴍʟᴇss ᴍᴜsɪᴄ ɪɴᴛᴇɢʀᴀᴛɪᴏɴ. Usᴇ ᴛʜᴇ MUSIC ʙᴜᴛᴛᴏɴ ᴛᴏ ᴀᴄᴄᴇss ᴀʟʟ ᴛʜᴇ ᴍᴜsɪᴄ-ʀᴇʟᴀᴛᴇᴅ ғᴜɴᴄᴛɪᴏɴᴀʟɪᴛɪᴇs, ғʀᴏᴍ sᴛʀᴇᴀᴍɪɴɢ ʏᴏᴜʀ ғᴀᴠᴏʀɪᴛᴇ sᴏɴɢs ᴛᴏ ᴄʀᴇᴀᴛɪɴɢ ᴘʟᴀʏʟɪsᴛs. Lᴏᴏᴋɪɴɢ ғᴏʀ ᴍᴏʀᴇ ᴏᴘᴛɪᴏɴs? Hɪᴛ ᴛʜᴇ ALL ʙᴜᴛᴛᴏɴ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴇᴠᴇʀʏᴛʜɪɴɢ ᴛʜɪs ʙᴏᴛ ᴄᴀɴ ᴏғғᴇʀ. Wʜᴇɴᴇᴠᴇʀ ʏᴏᴜ'ʀᴇ ʀᴇᴀᴅʏ, sɪᴍᴘʟʏ ᴛᴀᴘ HOME ᴛᴏ ʀᴇᴛᴜʀɴ ᴛᴏ ᴛʜᴇ ᴍᴀɪɴ ᴍᴇɴᴜ. Eɴɪᴏʏ ʏᴏᴜʀ ᴛɪᴍᴇ ᴡɪᴛʜ JBL Mᴜsɪᴄ Bᴏᴛ!**<blockquote><b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


@app.on_callback_query(filters.regex("music"))
async def music_callback(client: Client, callback_query: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="Aᴅᴍɪɴ", callback_data="music_callback hb1"),
                InlineKeyboardButton(text="Aᴜᴛʜ", callback_data="music_callback hb2"),
                InlineKeyboardButton(
                    text="Bʀᴏᴀᴅᴄᴀsᴛ", callback_data="music_callback hb3"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Bʟ-Cʜᴀᴛ", callback_data="music_callback hb4"
                ),
                InlineKeyboardButton(
                    text="Bʟ-Usᴇʀ", callback_data="music_callback hb5"
                ),
                InlineKeyboardButton(text="C-Pʟᴀʏ", callback_data="music_callback hb6"),
            ],
            [
                InlineKeyboardButton(text="G-Bᴀɴ", callback_data="music_callback hb7"),
                InlineKeyboardButton(text="Lᴏᴏᴘ", callback_data="music_callback hb8"),
                InlineKeyboardButton(
                    text="Mᴀɪɴᴛᴇɴᴀɴᴄᴇ", callback_data="music_callback hb9"
                ),
            ],
            [
                InlineKeyboardButton(text="Pɪɴɢ", callback_data="music_callback hb10"),
                InlineKeyboardButton(text="Pʟᴀʏ", callback_data="music_callback hb11"),
                InlineKeyboardButton(
                    text="Sʜᴜғғʟᴇ", callback_data="music_callback hb12"
                ),
            ],
            [
                InlineKeyboardButton(text="Sᴇᴇᴋ", callback_data="music_callback hb13"),
                InlineKeyboardButton(text="Sᴏɴɢ", callback_data="music_callback hb14"),
                InlineKeyboardButton(text="Sᴘᴇᴇᴅ", callback_data="music_callback hb15"),
            ],
            [InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data=f"feature")],
        ]
    )

    await callback_query.message.edit(
        "<blockquote><b>ʜᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴍᴜꜱɪᴄ ᴏᴘᴛɪᴏɴꜱ...<blockquote><b>", reply_markup=keyboard
    )


@app.on_callback_query(filters.regex("back_to_music"))
async def feature_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(
                text="💫 ᴀᴅᴅ ᴍᴇ ᴍᴏʀᴇ ❤️",
                url=f"https://t.me/{app.username}?startgroup=true",
            ),
        ],
        [
            InlineKeyboardButton(text="🎧 ᴍᴜsɪᴄ 🎧", callback_data="music"),
            InlineKeyboardButton(text="🤖 ᴍᴀɴᴇɢᴇᴍᴇɴᴛ 🤖", callback_data="settings_back_helper"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        "<blockquote><b>ʜᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ʙᴏᴛ ꜰᴇᴀᴛᴜʀᴇꜱ...<blockquote><b>", reply_markup=InlineKeyboardMarkup(keyboard)
    )


def back_to_music(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"music",
                ),
            ]
        ]
    )
    return upl


@app.on_callback_query(filters.regex("about"))
async def about_callback(client: Client, callback_query: CallbackQuery):
    buttons = [
        [
            InlineKeyboardButton(text="✨ ᴅᴇᴠᴇʟᴏᴘᴇʀ ✨", callback_data="developer"),
            InlineKeyboardButton(text="⚡ ғᴇᴀᴛᴜʀᴇ ⚡", callback_data="feature"),
        ],
        [
            InlineKeyboardButton(text="📝 ʙᴀsɪᴄ ɢᴜɪᴅᴇ 📓", callback_data="basic_guide"),
            InlineKeyboardButton(text="✉️ ᴅᴏɴᴀᴛᴇ ✉️", callback_data="donate"),
        ],
        [InlineKeyboardButton(text="🔙 Back", callback_data="go_to_start")],
    ]
    await callback_query.message.edit_text(
        "<blockquote><b>ʀᴇᴛᴜʀɴɪɴɢ ᴛᴏ ᴀʙᴏᴜᴛ ᴏᴘᴛɪᴏɴꜱ...<blockquote><b>", reply_markup=InlineKeyboardMarkup(buttons)
    )


# If the back button has different meanings in various panels, you can set different callbacks
@app.on_callback_query(filters.regex("support"))
async def back_button_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [
        [
            InlineKeyboardButton(text=" ᴄ❍ᴅᴇꝛ ", user_id=config.OWNER_ID[0]),
            InlineKeyboardButton(
                text="🗝️ ɢɪᴛʜᴜʙ 🗝️",
                url="https://github.com/txkuze",
            ),
        ],
        [
            InlineKeyboardButton(text="🗡️ ɢʀᴏᴜᴘ 🗡️", url=f"{config.SUPPORT_GROUP}"),
            InlineKeyboardButton(text="⚔️ ᴄʜᴀɴɴᴇʟ ⚔️", url=f"{config.SUPPORT_CHANNEL}"),
        ],
        [InlineKeyboardButton(text="✯ ʜᴏᴍᴇ ✯", callback_data="go_to_start")],
    ]

    await callback_query.message.edit_text(
        "<blockquote><b>ʜᴇʀᴇ ɪꜱ ᴛʜᴇ ꜱᴜᴘᴘᴏʀᴛ ᴍᴇɴᴜ...<blockquote><b>", reply_markup=InlineKeyboardMarkup(keyboard)
    )


@app.on_callback_query(filters.regex("donate"))
async def settings_back_callback(client: Client, callback_query: CallbackQuery):
    close = [[InlineKeyboardButton(text="✯ ᴄʟᴏsᴇ ✯", callback_data="close")]]
    await callback_query.message.reply_photo(
        photo=donate,
        caption=f"<blockquote><b>**sᴜᴘᴘᴏʀᴛ ᴍʏ ᴄᴏᴅɪɴɢ ᴊᴏᴜʀɴᴇʏ ʙʏ ᴅᴏɴᴀᴛɪɴɢ ᴅɪʀᴇᴄᴛʟʏ ᴛᴏ ʜᴇʟᴘ ᴇɴʜᴀɴᴄᴇ ᴍʏ ʙᴏᴛ's ғᴇᴀᴛᴜʀᴇs ᴀɴᴅ ᴅᴇᴠᴇʟᴏᴘᴍᴇɴᴛ.**\n\n**ʏᴏᴜʀ ᴄᴏɴᴛʀɪʙᴜᴛɪᴏɴ ᴡɪʟʟ ᴅɪʀᴇᴄᴛʟʏ ғᴜɴᴅ ᴛʜᴇ ᴄʀᴇᴀᴛɪᴏɴ ᴏғ ɪɴɴᴏᴠᴀᴛɪᴠᴇ, ᴜsᴇʀ-ғʀɪᴇɴᴅʟʏ ᴛᴏᴏʟs ᴀɴᴅ ᴇxᴄɪᴛɪɴɢ ʙᴏᴛ ᴄᴀᴘᴀʙɪʟɪᴛɪᴇs.**\n\n**sɪᴍᴘʟʏ sᴄᴀɴ ᴛʜᴇ ᴄᴏᴅᴇ ᴀɴᴅ ᴍᴀᴋᴇ ᴀ ᴘᴀʏᴍᴇɴᴛ—ɴᴏ ʜᴀssʟᴇ, ᴊᴜsᴛ ᴀ ǫᴜɪᴄᴋ ᴡᴀʏ ᴛᴏ sᴜᴘᴘᴏʀᴛ ᴀɴᴅ ʜᴇʟᴘ ʙʀɪɴɢ ɴᴇᴡ ғᴇᴀᴛᴜʀᴇs ᴛᴏ ʟɪғᴇ.**\n\n**ᴇᴠᴇʀʏ ᴅᴏɴᴀᴛɪᴏɴ, ʙɪɢ ᴏʀ sᴍᴀʟʟ, ɢᴏᴇs ᴀ ʟᴏɴɢ ᴡᴀʏ ɪɴ ᴘᴜsʜɪɴɢ ᴛʜɪs ᴘʀᴏᴊᴇᴄᴛ ғᴏʀᴡᴀʀᴅ. ᴛʜᴀɴᴋ ʏᴏᴜ ғᴏʀ ʙᴇɪɴɢ ᴀ ᴘᴀʀᴛ ᴏғ ᴛʜɪs ᴇxᴄɪᴛɪɴɢ ᴊᴏᴜʀɴᴇʏ!**<blockquote><b>",
        reply_markup=InlineKeyboardMarkup(close),
    )


@app.on_callback_query(filters.regex("basic_guide"))
async def settings_back_callback(client: Client, callback_query: CallbackQuery):
    keyboard = [[InlineKeyboardButton(text="✯ ʙᴀᴄᴋ ✯", callback_data="about")]]
    guide_text = f"<blockquote><b>ʜᴇʀᴇ ᴀʀᴇ ᴛʜᴇ ᴍᴜꜱɪᴄ ᴏᴘᴛɪᴏɴꜱ...<blockquote><b>**ʜᴇʏ! ᴛʜɪs ɪs ᴀ ǫᴜɪᴄᴋ ᴀɴᴅ sɪᴍᴘʟᴇ ɢᴜɪᴅᴇ ᴛᴏ ᴜsɪɴɢ** {app.mention} **🎉**\n\n**1. ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ 'ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʟᴀɴ' ʙᴜᴛᴛᴏɴ.**\n**2. sᴇʟᴇᴄᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɴᴀᴍᴇ.**\n**3. ɢʀᴀɴᴛ ᴛʜᴇ ʙᴏᴛ ᴀʟʟ ɴᴇᴄᴇssᴀʀʏ ᴘᴇʀᴍɪssɪᴏɴs ғᴏʀ sᴍᴏᴏᴛʜ ᴀɴᴅ ғᴜʟʟ ғᴜɴᴄᴛɪᴏɴᴀʟɪᴛʏ.**\n\n**ᴛᴏ ᴀᴄᴄᴇss ᴄᴏᴍᴍᴀɴᴅs, ʏᴏᴜ ᴄᴀɴ ᴄʜᴏᴏsᴇ ʙᴇᴛᴡᴇᴇɴ ᴍᴜsɪᴄ ᴏʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇs.**\n**ɪғ ʏᴏᴜ sᴛɪʟʟ ғᴀᴄᴇ ᴀɴʏ ɪssᴜᴇs, ғᴇᴇʟ ғʀᴇᴇ ᴛᴏ ʀᴇᴀᴄʜ ᴏᴜᴛ ғᴏʀ sᴜᴘᴘᴏʀᴛ ✨**<blockquote><b>"
    await callback_query.message.edit_text(
        text=guide_text, reply_markup=InlineKeyboardMarkup(keyboard)
)
        
