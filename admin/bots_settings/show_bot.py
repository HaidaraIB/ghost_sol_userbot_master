from telegram import (
    Chat,
    Update,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from common.common import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from start import start_command, admin_command
from admin.bots_settings.common import (
    build_bots_keyboard,
    build_update_bot_keyboard,
    stringify_bot_info,
    back_to_bot_settings,
)
from custom_filters import Owner
import models

(
    CHOOSE_BOT_TO_SHOW,
    CHOOSE_UPDATE_BOT,
    NEW_NAME,
) = range(3)


async def show_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        keyboard = build_bots_keyboard('s')
        if not isinstance(keyboard, InlineKeyboardMarkup) and len(keyboard) == 2:
            await update.callback_query.answer(
                text="ليس لديك بوتات",
                show_alert=True,
            )
            return
        await update.callback_query.edit_message_text(
            text="اختر البوت",
            reply_markup=keyboard,
        )
        return CHOOSE_BOT_TO_SHOW


async def choose_bot_to_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        context.user_data["bot_id_to_show"] = int(update.callback_query.data.split("_")[-1])
        bot = models.Bot.get_one(bot_id=int(context.user_data["bot_id_to_show"]))
        keyboard = build_update_bot_keyboard(bot)
        keyboard.append(build_back_button("back_to_choose_bot_to_show"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_bot_info(bot),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_UPDATE_BOT


back_to_choose_bot_to_show = show_bots


async def choose_update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        bot = models.Bot.get_one(bot_id=context.user_data["bot_id_to_show"])
        if update.callback_query.data.startswith("activate_bot"):
            await models.Bot.update(
                bot_id=context.user_data["bot_id_to_show"], on=(not bot.on)
            )
            updated_bot = models.Bot.get_one(bot_id=context.user_data["bot_id_to_show"])

            await update.callback_query.answer(
                text="تم التعديل بنجاح ✅",
                show_alert=True,
            )

            keyboard = build_update_bot_keyboard(updated_bot)
            keyboard.append(build_back_button("back_to_choose_bot_to_show"))
            keyboard.append(back_to_admin_home_page_button[0])
            await update.callback_query.edit_message_text(
                text=stringify_bot_info(updated_bot),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return CHOOSE_UPDATE_BOT
        elif update.callback_query.data == "update_bot_name":
            back_buttons = [
                build_back_button("back_to_choose_bot_to_show"),
                back_to_admin_home_page_button[0],
            ]
            await update.callback_query.edit_message_text(
                text="أرسل الاسم الجديد",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
            return NEW_NAME


async def get_new_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        await models.Bot.update(
            bot_id=context.user_data["bot_id_to_show"], name=update.message.text
        )
        updated_bot = models.Bot.get_one(bot_id=context.user_data["bot_id_to_show"])

        await update.message.reply_text(text="تم التعديل بنجاح ✅")

        keyboard = build_update_bot_keyboard(updated_bot)
        keyboard.append(build_back_button("back_to_choose_bot_to_show"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.message.reply_text(
            text=stringify_bot_info(updated_bot),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_UPDATE_BOT


show_bot_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=show_bots,
            pattern="^show bots$",
        )
    ],
    states={
        CHOOSE_BOT_TO_SHOW: [CallbackQueryHandler(choose_bot_to_show, "^s_bot")],
        CHOOSE_UPDATE_BOT: [
            CallbackQueryHandler(choose_update_bot, "^((update_bot)|(activate_bot))")
        ],
        NEW_NAME: [
            MessageHandler(
                filters=filters.TEXT & ~filters.COMMAND,
                callback=get_new_name,
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_bot_settings,
            pattern="^back_to_bot_settings$",
        ),
        CallbackQueryHandler(
            back_to_choose_bot_to_show, "^back_to_choose_bot_to_show$"
        ),
        back_to_admin_home_page_handler,
        start_command,
        admin_command,
    ],
)
