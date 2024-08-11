from telethon import events
from telethon.tl.patched import Message
from ClientSingleton import ClientSingleton
from common.constants import *
import models
import re


def extract_matches(net, text):
    matches = set()
    if net in ["solana", "both"]:
        if not any(t in text for t in ["SOL", "solana"]):
            return
        pattern = re.compile(SOLANA_LINK_PATTERN)
        solana_match = re.findall(pattern, text)
        if not solana_match:
            pattern = re.compile(SOLANA_SA_ADDRESS_PATTERN)
            solana_match = re.findall(pattern, text)
        if solana_match:
            matches.add(solana_match[0])
    if net in ["eth", "both"]:
        if not any(t in text for t in ["ETH", "ethereum"]):
            return
        pattern = re.compile(ETH_LINK_PATTERN)
        eth_match = re.findall(pattern, text)
        if not eth_match:
            pattern = re.compile(ETH_SA_ADDRESS_PATTERN)
            eth_match = re.findall(pattern, text)
        if eth_match:
            matches.add(eth_match[0])
    return matches


async def copy_messages(event: events.NewMessage.Event | events.Album.Event):
    if event.forward:
        return
    FROM = models.Channel.get_all(for_on=True)
    if event.chat_id not in [ch.id for ch in FROM]:
        return

    message: Message = event.message
    ch = models.Channel.get_one(ch_id=event.chat_id)
    if message.is_reply and not ch.for_rep:
        return

    matches = extract_matches(net=ch.net, text=message.message)
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
