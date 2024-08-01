from telegram import Update
from telegram.ext.filters import UpdateFilter
import os


class Owner(UpdateFilter):
    def filter(self, update: Update):
        return update.effective_user.id == int(os.getenv("OWNER_ID"))
