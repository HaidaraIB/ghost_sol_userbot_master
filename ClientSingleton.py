import os
from telethon import TelegramClient
import asyncio

class ClientSingleton(TelegramClient):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:

            cls._instance = TelegramClient(
                session=os.getenv("SESSION"),
                api_id=int(os.getenv("API_ID")),
                api_hash=os.getenv("API_HASH"),
                
            ).start(phone=os.getenv("PHONE"))
        return cls._instance
    
    @staticmethod
    async def request_updates():
        client = ClientSingleton()
        while True:
            await client.catch_up()
            await asyncio.sleep(1)

