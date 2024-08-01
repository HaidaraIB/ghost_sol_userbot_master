from telegram import (
    Chat,
    Update,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)
from admin.channels_settings.common import (
    CHOOSE_CHANNEL_TO_REMOVE_TEXT,
    back_to_channel_settings,
    build_channels_keyboard,
)
from start import start_command, admin_command
from common.back_to_home_page import back_to_admin_home_page_handler
from custom_filters import Admin
import models


CHOOSE_CHANNEL_TO_REMOVE = 0


async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_channels_keyboard()

        if not keyboard:
            await update.callback_query.answer(
                text="ليس لديك قنوات بعد",
                show_alert=True,
            )
            return

        if update.callback_query.data[1:].isnumeric():
            await models.Channel.remove(channel_id=int(update.callback_query.data))
            await update.callback_query.answer(
                text="تمت إزالة القناة بنجاح ✅",
                show_alert=True,
            )
        await update.callback_query.edit_message_text(
            text=CHOOSE_CHANNEL_TO_REMOVE_TEXT,
            reply_markup=keyboard,
        )
        return CHOOSE_CHANNEL_TO_REMOVE


remove_channel_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_channel,
            pattern="^remove channel$",
        ),
    ],
    states={
        CHOOSE_CHANNEL_TO_REMOVE: [
            CallbackQueryHandler(
                remove_channel,
                "^-?\d+$",
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_channel_settings,
            pattern="^back_to_channel_settings$",
        ),
        admin_command,
        start_command,
        back_to_admin_home_page_handler,
    ],
)
