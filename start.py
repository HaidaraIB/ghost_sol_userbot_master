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
import asyncio

from custom_filters import Admin

from ClientSingleton import ClientSingleton

from common.decorators import (
    add_new_user_dec,
)
from common.common import (
    build_admin_keyboard,
    request_buttons,
)


async def inits(app: Application):
    asyncio.create_task(ClientSingleton.request_updates())
    await models.Admin.add_new_admin(admin_id=int(os.getenv("OWNER_ID")))


@add_new_user_dec
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
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
