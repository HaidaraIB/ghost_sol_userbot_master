from telegram import (
    Chat,
    Update,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)
from admin.bots_settings.common import (
    build_bots_keyboard,
    back_to_bot_settings,
    CHOOSE_BOT_TO_REMOVE_TEXT,
)
from start import start_command, admin_command
from common.back_to_home_page import back_to_admin_home_page_handler
from custom_filters import Admin
import models


CHOOSE_BOT_TO_REMOVE = 0


async def remove_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_bots_keyboard()

        if not keyboard:
            await update.callback_query.answer(
                text="ليس لديك بوتات بعد",
                show_alert=True,
            )
            return

        if update.callback_query.data[1:].isnumeric():
            await models.Bot.remove(bot_id=int(update.callback_query.data))
            await update.callback_query.answer(
                text="تمت إزالة البوت بنجاح ✅",
                show_alert=True,
            )
        await update.callback_query.edit_message_text(
            text=CHOOSE_BOT_TO_REMOVE_TEXT,
            reply_markup=keyboard,
        )
        return CHOOSE_BOT_TO_REMOVE


remove_bot_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=remove_bot,
            pattern="^remove bot$",
        ),
    ],
    states={
        CHOOSE_BOT_TO_REMOVE: [
            CallbackQueryHandler(
                remove_bot,
                "^-?\d+$",
            ),
        ]
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_bot_settings,
            pattern="^back_to_channel_settings$",
        ),
        admin_command,
        start_command,
        back_to_admin_home_page_handler,
    ],
)