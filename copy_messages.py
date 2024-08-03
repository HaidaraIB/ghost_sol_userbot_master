from telethon import events
from telethon.tl.patched import Message
from ClientSingleton import ClientSingleton
from common.constants import *
import models
import re


def extract_matches(net, text):
    matches = []
    if net in ["solana", "both"]:
        solana_match = re.findall(SOLANA_LINK_PATTERN, text)
        if not solana_match:
            solana_match = re.findall(SOLANA_SA_ADDRESS_PATTERN, text)
        if solana_match:
            matches.append(solana_match[0])
    if net in ["eth", "both"]:
        eth_match = re.findall(ETH_LINK_PATTERN, text)
        if not eth_match:
            eth_match = re.findall(ETH_SA_ADDRESS_PATTERN, text)
        if eth_match:
            matches.append(eth_match[0])
    return matches


async def copy_messages(event: events.NewMessage.Event | events.Album.Event):
    FROM = models.Channel.get_all(for_on=True)
    if event.chat_id not in [ch.id for ch in FROM]:
        return

    gallery = getattr(event, "messages", None)
    if event.grouped_id and not gallery:
        return

    message: Message = event.message
    ch = models.Channel.get_one(ch_id=event.chat_id)

    if message.is_reply and not ch.for_rep:
        return
    
    matches = extract_matches(net=ch.net, text=message.text)
    if not matches:
        return

    active_bot = models.Bot.get_one(active=True)
    if not active_bot:
        return

    for m in matches:
        msg = await ClientSingleton().send_message(
            active_bot.id,
            m,
        )
        await models.Message.add(
            from_message_id=message.id,
            to_message_id=msg.id,
            from_channel_id=event.chat_id,
            to_channel_id=active_bot.id,
        )
    raise events.StopPropagation
