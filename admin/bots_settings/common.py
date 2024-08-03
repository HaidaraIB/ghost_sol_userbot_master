from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Chat,
    Update,
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
from common.back_to_home_page import back_to_admin_home_page_button
from common.common import build_back_button
import models


CHOOSE_BOT_TO_REMOVE_TEXT = "اختر من القائمة أدناه البوت الذي تريد إزالته."


bot_settings_keyboard = [
    [
        InlineKeyboardButton(text="إضافة بوت ➕", callback_data="add bot"),
        InlineKeyboardButton(text="حذف بوت ✖️", callback_data="remove bot"),
    ],
    [InlineKeyboardButton(text="قائمة البوتات 📋", callback_data="show bots")],
    back_to_admin_home_page_button[0],
]

def build_update_bot_keyboard(bot:models.Bot):
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"تعديل الاسم",
                callback_data="update_bot_name"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🟢 فعال" if bot.on  else "🔴 غير فعال",
                callback_data="activate_bot"
            ),
        ]
    ]
    return keyboard

def stringify_bot_info(bot:models.Bot):
    return (
        f"آيدي البوت:\n<code>{bot.id}</code>\n"
        f"اسم البوت: <b>{bot.name}</b>\n"
    )

async def back_to_bot_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد:",
            reply_markup=InlineKeyboardMarkup(bot_settings_keyboard),
        )
        if update.callback_query.data.startswith("back"):
            return ConversationHandler.END


def build_bots_keyboard():
    bots = models.Bot.get_all()
    if not bots:
        return False
    bots_keyboard = [
        [InlineKeyboardButton(text=f"{bot.name} {"🟢" if bot.on else ""}", callback_data=str(bot.id))]
        for bot in bots
    ]
    bots_keyboard.append(build_back_button("back_to_bot_settings"))
    bots_keyboard.append(back_to_admin_home_page_button[0])
    return InlineKeyboardMarkup(bots_keyboard)


bot_settings_handler = CallbackQueryHandler(
    back_to_bot_settings,
    "^bot_settings$"
)
