from telegram import (
    Chat,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
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

from common.common import build_admin_keyboard, build_back_button
from admin.channels_settings.common import back_to_channel_settings
from custom_filters import Owner
import models
from common.constants import *
from start import admin_command, start_command
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_admin_home_page_button,
)
from ClientSingleton import ClientSingleton
from telethon.hints import Entity
(
    NEW_CHANNEL,
    CHOOSE_NET,
    FOR_REP,
) = range(3)


async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر القناة التي تريد إضافتها بالضغط على الزر أدناه\n\n"
                "يمكنك إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار قناة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=6, chat_is_channel=True
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return NEW_CHANNEL


async def new_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        net_keyboard = [
            [
                InlineKeyboardButton(text="سولانا", callback_data="add_channel_solana"),
                InlineKeyboardButton(text="إيثيريوم", callback_data="add_channel_eth"),
            ],
            [
                InlineKeyboardButton(text="كلاهما", callback_data="add_channel_both"),
            ],
            build_back_button("back_to_new_channel"),
            back_to_admin_home_page_button[0],
        ]
        if update.message:
            channel_id = update.effective_message.chat_shared.chat_id

            if models.Channel.get_one(ch_id=channel_id):
                await update.message.reply_text(text="هذه القناة مضافة بالفعل")
                return

            context.user_data["add_channel_chat_id"] = channel_id
            context.user_data["add_channel_chat"] = (
                await ClientSingleton().get_entity(entity=channel_id)
            )
            await update.message.reply_text(
                text="تم العثور على القناة ✅.",
                reply_markup=ReplyKeyboardRemove(),
            )
            await update.message.reply_text(
                text="اختر الشبكة",
                reply_markup=InlineKeyboardMarkup(net_keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text="اختر الشبكة",
                reply_markup=InlineKeyboardMarkup(net_keyboard),
            )

        return CHOOSE_NET


back_to_new_channel = add_channel


async def choose_net(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        if not update.callback_query.data.startswith("back"):
            context.user_data["add_channel_net"] = update.callback_query.data.split(
                "_"
            )[-1]
        for_rep_keyboard = [
            [
                InlineKeyboardButton(
                    text="نعم",
                    callback_data="yes_for_rep",
                ),
                InlineKeyboardButton(
                    text="لا",
                    callback_data="no_for_rep",
                ),
            ],
            build_back_button("back_to_choose_net"),
            back_to_admin_home_page_button[0],
        ]
        await update.callback_query.edit_message_text(
            text="تحويل الردود",
            reply_markup=InlineKeyboardMarkup(for_rep_keyboard),
        )
        return FOR_REP


back_to_choose_net = new_channel


async def for_rep(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        chat: Entity = context.user_data["add_channel_chat"]
        await models.Channel.add(
            channel_id=context.user_data["add_channel_chat_id"],
            name=(
                chat.title
                if chat.title
                else (
                    chat.first_name + chat.last_name
                    if chat.last_name
                    else chat.first_name
                )
            ),
            username="@" + chat.username if chat.username else "لا يوجد",
            net=context.user_data["add_channel_net"],
            for_rep=update.callback_query.data.startswith("yes"),
        )
        await update.callback_query.edit_message_text(
            text="تمت إضافة القناة بنجاح، تحويل الرسائل قيد التفعيل بشكل افتراضي، يمكنك التعديل على القناة من خلال زر قائمة القنوات.",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_channel_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_channel,
            pattern="^add channel$",
        ),
    ],
    states={
        NEW_CHANNEL: [
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=new_channel,
            ),
        ],
        CHOOSE_NET: [
            CallbackQueryHandler(choose_net, "^add_channel_((solana)|(eth)|(both))$")
        ],
        FOR_REP: [CallbackQueryHandler(for_rep, "^((yes)|(no))_for_rep$")],
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_channel_settings,
            pattern="^back_to_channel_settings$",
        ),
        CallbackQueryHandler(
            callback=back_to_choose_net,
            pattern="^back_to_choose_net$",
        ),
        CallbackQueryHandler(
            callback=back_to_new_channel,
            pattern="^back_to_new_channel$",
        ),
        admin_command,
        start_command,
        back_to_admin_home_page_handler,
    ],
)
