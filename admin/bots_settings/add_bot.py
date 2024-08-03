from telegram import (
    Chat,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestUsers,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from admin.bots_settings.common import back_to_bot_settings
from common.common import build_admin_keyboard, build_back_button
from custom_filters import Owner
import models
from common.constants import *
from start import admin_command, start_command
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)

(
    NEW_BOT,
    NAME,
    ACTIVATE,
) = range(3)


async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر البوت الذي تريد إضافته بالضغط على الزر أدناه\n\n"
                "يمكنك إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار بوت",
                            request_users=KeyboardButtonRequestUsers(
                                request_id=7, user_is_bot=True
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_BOT


async def new_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        back_buttons = [
            build_back_button("back_to_new_bot"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            bot_id = update.effective_message.users_shared.users[0].user_id

            if models.Bot.get_one(bot_id=bot_id):
                await update.message.reply_text(text="هذه القناة مضافة بالفعل")
                return

            context.user_data["add_bot_id"] = bot_id
            await update.message.reply_text(
                text="تم العثور على البوت ✅",
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text="أرسل اسم هذا البوت",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        else:
            await update.callback_query.edit_message_text(
                text="أرسل اسم هذا البوت",
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        return NAME


back_to_new_bot = add_bot


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        keyboard = [
            [
                InlineKeyboardButton(text="نعم", callback_data="yes_activate_bot"),
                InlineKeyboardButton(text="لا", callback_data="no_activate_bot"),
            ],
            build_back_button("back_to_get_name"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            context.user_data["add_bot_name"] = update.message.text
            await update.message.reply_text(
                text="هل تريد تفعيل البوت؟", reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.callback_query.edit_message_text(
                text="هل تريد تفعيل البوت؟", reply_markup=InlineKeyboardMarkup(keyboard)
            )
        return ACTIVATE


back_to_get_name = new_bot


async def activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        await models.Bot.add(
            bot_id=context.user_data["add_bot_id"],
            name=context.user_data["add_bot_name"],
        )
        if update.callback_query.data.startswith("yes"):
            await models.Bot.update(
                bot_id=context.user_data["add_bot_id"],
                on=True,
            )
        await update.callback_query.edit_message_text(
            text="تمت إضافة البوت بنجاح، يمكنك التعديل عليه من خلال زر قائمة البوتات.",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_bot_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_bot,
            pattern="^add bot$",
        ),
    ],
    states={
        NEW_BOT: [
            MessageHandler(
                filters=filters.StatusUpdate.USERS_SHARED,
                callback=new_bot,
            ),
        ],
        NAME: [
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=get_name)
        ],
        ACTIVATE: [
            CallbackQueryHandler(
                activate,
                "^((yes)|(no))_activate_bot$",
            )
        ],
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_bot_settings,
            pattern="^back_to_bot_settings$",
        ),
        CallbackQueryHandler(
            callback=back_to_new_bot,
            pattern="^back_to_new_bot$",
        ),
        admin_command,
        start_command,
        back_to_admin_home_page_handler,
    ],
)
