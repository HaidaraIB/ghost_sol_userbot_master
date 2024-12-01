from telethon import events
from telethon.tl.patched import Message
from ClientSingleton import ClientSingleton
from common.constants import *
import models
import re


def find_matches(link_pattern, sa_address_pattern, text):
    pattern = re.compile(link_pattern)
    match = re.findall(pattern, text)
    if not match:
        pattern = re.compile(sa_address_pattern)
        match = re.findall(pattern, text)
    return match


def extract_matches(net, text):
    matches = set()
    if net in ["eth", "both"]:
        eth_match = find_matches(
            ETH_LINK_PATTERN,
            ETH_SA_ADDRESS_PATTERN,
            text,
        )
        if eth_match:
            matches.add(eth_match[0])
    if net in ["solana", "both"]:
        if net == "both" and eth_match:
            return
        eth_match = find_matches(
            ETH_LINK_PATTERN,
            ETH_SA_ADDRESS_PATTERN,
            text,
        )
        if eth_match:
            return
        solana_match = find_matches(
            SOLANA_LINK_PATTERN,
            SOLANA_SA_ADDRESS_PATTERN,
            text,
        )
        if solana_match:
            matches.add(solana_match[0])
    return matches


async def copy_messages(
    event: events.NewMessage.Event | events.Album.Event | events.MessageEdited.Event,
):
    if event.forward:
        return

    FROM = models.Channel.get_all(for_on=True)
    if event.chat_id not in [ch.id for ch in FROM]:
        return

    active_bot = models.Bot.get_one(active=True)
    if not active_bot:
        return
    
    message: Message = event.message
    if models.Message.get_one(
        from_message_id=message.id,
        from_channel_id=event.chat_id,
        to_channel_id=active_bot.id,
    ):
        return

    ch = models.Channel.get_one(ch_id=event.chat_id)
    if message.is_reply and not ch.for_rep:
        return

    matches = extract_matches(net=ch.net, text=message.message)
    if not matches:
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
