from telegram import (
    Update,
)

from telegram.ext import ContextTypes

import functools
import models


def check_if_user_banned_dec(func):
    @functools.wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = models.User.get_user(user_id=update.effective_user.id)
        if user.is_banned:
            return
        await func(update, context, *args, **kwargs)

    return wrapper
