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

CHOOSE_CHANNEL_TO_REMOVE_TEXT = "اختر من القائمة أدناه القناة التي تريد إزالتها."

channel_settings_keyboard = [
    [
        InlineKeyboardButton(text="إضافة قناة ➕", callback_data="add channel"),
        InlineKeyboardButton(text="حذف قناة ✖️", callback_data="remove channel"),
    ],
    [InlineKeyboardButton(text="قائمة القنوات", callback_data="show channels")],
    back_to_admin_home_page_button[0],
]


def build_update_channel_keyboard(channel:models.Channel):
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"إيثيريوم {"🟢" if channel.net in ["eth", 'both'] else "🔴"}",
                callback_data="update_net_eth"
            ),
            InlineKeyboardButton(
                text=f"سولانا {"🟢" if channel.net in ["solana", 'both'] else "🔴"}",
                callback_data="update_net_solana"
            ),
        ],
        [
            InlineKeyboardButton(
                text=f"تفعيل التحويل{"🟢" if channel.for_on else "🔴"}",
                callback_data="update_for_on"
            ),
            InlineKeyboardButton(
                text=f"تحويل الردود {"🟢" if channel.for_rep else "🔴"}",
                callback_data="update_for_rep"
            ),
        ]
    ]
    return keyboard

def stringify_channel_info(channel:models.Channel):
    return (
        f"آيدي القناة:\n<code>{channel.id}</code>\n"
        f"اسم القناة: <b>{channel.name}</b>\n"
        f"اليوزر: {channel.username}\n"
        f"الرابط: {channel.link}\n"
        f"الشبكة: <b>{channel.net}</b>\n"
        f"التحويل: {"🟢" if channel.for_rep else "🔴"}\n"
    )

async def back_to_channel_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="هل تريد:",
            reply_markup=InlineKeyboardMarkup(channel_settings_keyboard),
        )
        if update.callback_query.data.startswith("back"):
            return ConversationHandler.END


def build_channels_keyboard():
    channels = models.Channel.get_all()
    if not channels:
        return False
    channels_keyboard = [
        [InlineKeyboardButton(text=str(channel.name), callback_data=str(channel.id))]
        for channel in channels
    ]
    channels_keyboard.append(build_back_button("back_to_channel_settings"))
    channels_keyboard.append(back_to_admin_home_page_button[0])
    return InlineKeyboardMarkup(channels_keyboard)


channel_settings_handler = CallbackQueryHandler(
    back_to_channel_settings,
    "^channel_settings$"
)
