from telegram import (
    Chat,
    Update,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
)
from common.common import build_back_button
from common.back_to_home_page import (
    back_to_admin_home_page_button,
    back_to_admin_home_page_handler,
)
from start import start_command, admin_command
from admin.channels_settings.common import (
    stringify_channel_info,
    build_channels_keyboard,
    build_update_channel_keyboard,
    back_to_channel_settings,
)
from custom_filters import Owner
import models

(
    CHOOSE_CHANNEL_TO_SHOW,
    CHOOSE_UPDATE_CHANNEL,
) = range(2)


async def show_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        keyboard = build_channels_keyboard('s')
        if not isinstance(keyboard, InlineKeyboardMarkup) and len(keyboard) == 2:
            await update.callback_query.answer(
                text="ليس لديك قنوات",
                show_alert=True,
            )
            return

        await update.callback_query.edit_message_text(
            text="اختر القناة",
            reply_markup=keyboard,
        )
        return CHOOSE_CHANNEL_TO_SHOW


async def choose_channel_to_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        context.user_data["ch_id_to_show"] = int(update.callback_query.data.split("_")[-1])
        ch = models.Channel.get_one(ch_id=context.user_data["ch_id_to_show"])
        keyboard = build_update_channel_keyboard(ch)
        keyboard.append(build_back_button("back_to_choose_channel_to_show"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_channel_info(ch),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_UPDATE_CHANNEL


back_to_choose_channel_to_show = show_channels


async def choose_update_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Owner().filter(update):
        ch = models.Channel.get_one(ch_id=context.user_data["ch_id_to_show"])
        if update.callback_query.data.startswith("update_net"):
            net = update.callback_query.data.split("_")[-1]
            if ch.net == net:
                await update.callback_query.answer(
                    text="يجب أن يكون لكل قناة شبكة واحدة مفعلة على الأقل",
                    show_alert=True,
                )
                return
            elif ch.net == "both":
                await models.Channel.update(
                    ch_id=ch.id, net="eth" if net == "solana" else "solana"
                )
            else:
                await models.Channel.update(ch_id=ch.id, net="both")

        elif update.callback_query.data == "update_for_rep":
            await models.Channel.update(ch_id=ch.id, for_rep=(not ch.for_rep))
        elif update.callback_query.data == "update_for_on":
            await models.Channel.update(ch_id=ch.id, for_on=(not ch.for_on))

        updated_ch = models.Channel.get_one(ch_id=context.user_data["ch_id_to_show"])

        await update.callback_query.answer(
            text="تم التعديل بنجاح ✅",
            show_alert=True,
        )

        keyboard = build_update_channel_keyboard(updated_ch)
        keyboard.append(build_back_button("back_to_choose_channel_to_show"))
        keyboard.append(back_to_admin_home_page_button[0])
        await update.callback_query.edit_message_text(
            text=stringify_channel_info(updated_ch),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return CHOOSE_UPDATE_CHANNEL


show_channel_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=show_channels,
            pattern="^show channels$",
        )
    ],
    states={
        CHOOSE_CHANNEL_TO_SHOW: [
            CallbackQueryHandler(choose_channel_to_show, "^s_ch")
        ],
        CHOOSE_UPDATE_CHANNEL: [CallbackQueryHandler(choose_update_channel, "^update")],
    },
    fallbacks=[
        CallbackQueryHandler(
            callback=back_to_channel_settings,
            pattern="^back_to_channel_settings$",
        ),
        CallbackQueryHandler(
            back_to_choose_channel_to_show, "^back_to_choose_channel_to_show$"
        ),
        back_to_admin_home_page_handler,
        start_command,
        admin_command,
    ],
)
