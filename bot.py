# -*- coding: utf-8 -*-
# < (c) @TheZeusxD , https://t.me/TheZeusxD >
# invitesApproval, 2021.

# Paid source, re-distributing without contacting the code owner is NOT allowed.

import logging
import os
from decouple import config
from telethon import functions, types
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from telethon.errors.rpcerrorlist import ChatAdminRequiredError

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)

log = logging.getLogger("invitesApproval")

log.info("\n\nStarting...")

# getting the vars
try:
    API_ID = config("API_ID", default=None, cast=int)
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    owonerz = config("OWNERS")
    SESSION = config("SESSION")
except Exception as e:
    log.warning("Missing config vars {}".format(e))
    exit(1)

OWNERS = [int(i) for i in owonerz.split(" ")]
OWNERS.append(719195224) if 719195224 not in OWNERS else None

# connecting the user client
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except Exception as e:
    log.warning(e)
    exit(1)

# connecting the bot client
try:
    bot = TelegramClient(None, 6, "eb06d4abfb49dc3eeb1aeb98ae0f581e").start(
        bot_token=BOT_TOKEN
    )
except Exception as e:
    logging.warning(e)
    exit(1)


async def get_waiting(chat_id):
    try:
        users = await client(
            functions.messages.GetChatInviteImportersRequest(
                requested=True,
                peer=chat_id,
                limit=0,
                offset_date=0,
                offset_user=types.InputPeerEmpty(),
            )
        )
    except ChatAdminRequiredError:
        me = await client.get_me()
        return (
            "Please make [{}](tg://user?id={}) admin here!".format(
                me.first_name, me.id
            ),
            [],
        )
    if users.count == 0:
        return "No user in waiting list!", []
    userids = [i.user_id for i in users.importers]
    return "**Users in waiting list**: {}\n\n".format(users.count), userids


@bot.on(
    events.NewMessage(incoming=True, pattern="^/start$", func=lambda e: e.is_private)
)
async def starters(event):
    if event.sender_id in OWNERS:
        await event.reply(
            "I'm Online.\n\nCommands:\n/auths\n/approveall\n/disapproveall\n/getwaiting"
        )
    else:
        await event.reply(
            "Invites approval bot.\nAccept all group/channel join invites in one go!.",
            buttons=Button.url("Buy one now!", url="https://t.me/TheZeusxD"),
        )


@bot.on(events.NewMessage(incoming=True, pattern="^/getwaiting", from_users=OWNERS))
async def reply_waits(event):
    cid = chat = None
    if event.is_private:
        try:
            cid = event.text.split(" ")[1]
        except IndexError:
            await event.reply(
                "Please provide a chat ID or username, or use this command in that chat/channel."
            )
            return
    else:
        cid = event.chat_id
    try:
        cid = int(cid)
        chat = (await client.get_entity(cid)).id
    except ValueError:
        chat = (await client.get_entity(cid)).id
    msg, users = await get_waiting(chat)
    await event.reply(msg)


@bot.on(
    events.NewMessage(
        incoming=True,
        from_users=OWNERS,
        pattern="^/approveall",
    )
)
async def approvealll(event):
    cid = chat = None
    xx = await event.reply("Please wait...")
    if event.is_private:
        try:
            cid = event.text.split(" ")[1]
        except IndexError:
            await xx.edit(
                "Please provide a chat ID or username, or use this command in that chat/channel."
            )
            return
    else:
        cid = event.chat_id
    try:
        cid = int(cid)
        chat = (await client.get_entity(cid)).id
    except ValueError:
        chat = (await client.get_entity(cid)).id
    msg, users = await get_waiting(chat)
    if msg.startswith("Please") or msg.startswith("No"):
        await xx.edit(msg)
        return
    else:
        dn = fail = 0
        err = None
        while len(users) > 0:
            for i in users:
                try:
                    await client(
                        functions.messages.HideChatJoinRequestRequest(
                            chat, user_id=int(i), approved=True
                        )
                    )
                    dn += 1
                except Exception as e:
                    fail += 1
                    err = e
            msg, users = await get_waiting(chat)
            if msg.startswith("Please") or msg.startswith("No"):
                await xx.edit(msg)
                break
        msg = "__Approved {} user(s).__".format(dn)
        if fail != 0:
            msg += "\n__Failed to approve {} user(s).__".format(fail)
            msg += "\n\n**ERROR**: {}".format(err)
    await xx.edit(msg)


@bot.on(
    events.NewMessage(
        incoming=True,
        from_users=OWNERS,
        pattern="^/disapproveall",
    )
)
async def approvealll(event):
    cid = chat = None
    if event.is_private:
        try:
            cid = event.text.split(" ")[1]
        except IndexError:
            await event.reply(
                "Please provide a chat ID or username, or use this command in that chat/channel."
            )
            return
    else:
        cid = event.chat_id
    try:
        cid = int(cid)
        chat = (await client.get_entity(cid)).id
    except ValueError:
        chat = (await client.get_entity(cid)).id
    msg, users = await get_waiting(chat)
    if msg.startswith("Please") or msg.startswith("No"):
        await event.reply(msg)
        return
    else:
        dn = fail = 0
        err = None
        for i in users:
            try:
                await client(
                    functions.messages.HideChatJoinRequestRequest(
                        chat, user_id=int(i), approved=False
                    )
                )
                dn += 1
            except Exception as e:
                fail += 1
                err = e
        msg = "__Disapproved {} user(s).__".format(dn)
        if fail != 0:
            msg += "\n__Failed to disapprove {} user(s).__".format(fail)
            msg += "\n\n**ERROR**: {}".format(err)
    await event.reply(msg)


@bot.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^/auths$"))
async def all_auths(event):
    msg = "**List of auth users**:\n\n"
    for i in OWNERS:
        msg += "[{}](tg://user?id={})\n".format(i, i)
    if len(msg) > 4096:
        with open("auths.txt", "w") as f:
            f.write(msg.replace("*", ""))
        await event.reply("**Auth users**", file="auths.txt")
        os.remove("auth.txt")
    else:
        await event.reply(msg)


log.info("\n\nBot has started.\n(c) @xditya.")
bot.run_until_disconnected()
