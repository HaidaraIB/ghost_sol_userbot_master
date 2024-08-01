from telegram import (
    Update,
    Chat,
    ReplyKeyboardMarkup,
    BotCommand,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    ConversationHandler,
)


import os
import models
from common.force_join import check_if_user_member

from custom_filters import Admin
from common.decorators import check_if_user_banned_dec, add_new_user_dec
from common.common import (
    build_user_keyboard,
    build_admin_keyboard,
    request_buttons,
)


async def inits(app: Application):
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))


@add_new_user_dec
@check_if_user_banned_dec
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await context.bot.set_my_commands(
            commands=[
                BotCommand(
                    command="start",
                    description="home page",
                ),
            ]
        )

        member = await check_if_user_member(update=update, context=context)
        if not member:
            return

        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=build_user_keyboard(),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await context.bot.set_my_commands(
            commands=[
                BotCommand(
                    command="start",
                    description="home page",
                ),
                BotCommand(
                    command="admin",
                    description="control panel",
                ),
            ]
        )
        if (
            not context.user_data.get("request_keyboard_hidden", None)
            or not context.user_data["request_keyboard_hidden"]
        ):
            context.user_data["request_keyboard_hidden"] = False
            await update.message.reply_text(
                text="أهلاً بك...",
                reply_markup=ReplyKeyboardMarkup(
                    request_buttons,
                    resize_keyboard=True,
                ),
            )
        else:
            await update.message.reply_text(
                text="أهلاً بك...",
                reply_markup=ReplyKeyboardRemove(),
            )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
