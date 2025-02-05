from telethon import events
import json as jn
import telethon as th
import asyncio

import src.db as db
import src.job as job 

PATH = "./dev" # Change to ./ 

tg_config = jn.load(open(f"{PATH}/configs/conf.json", "r", encoding="utf-8"))
msgs_conf = jn.load(open("./configs/messages.json", "r", encoding="utf-8"))

database = db.DataBase(f"{PATH}/db/database.json")
client = th.TelegramClient( session = tg_config["session_path"], api_id = tg_config["api_id"], api_hash = tg_config["api_hash"] )

@client.on(events.NewMessage()) #outgoing=False
async def first(event: th.types.UpdateNewMessage):

    text: str = event.text
    user_id: str = "-1"

    try:
        if type(event.original_update).__name__ == "UpdateNewChannelMessage":
            user_id = str(event.original_update.message.from_id.user_id)
        elif type(event.original_update).__name__ == "UpdateShortChatMessage":
            user_id = str(event.original_update.from_id)
    except Exception as ex:
        print(f"\rError: {ex}")

    if user_id == "-1": return

    if text.startswith(">smth"):
        cmd = text.split()[1]

        if cmd in msgs_conf["help"]["trigers"]:
            await event.reply(msgs_conf["help"]["value"])

        if cmd in msgs_conf["job"]["trigers"]:
            await event.reply(job.get_job(user_id, text.split()[2:], msgs_conf, database))

        if cmd in msgs_conf["mine"]["trigers"]:
            await event.reply(job.mine(user_id, text.split()[2:], msgs_conf, database))

        if cmd in msgs_conf["balance"]["trigers"]:
            await event.reply(job.balance(user_id, text.split()[2:], msgs_conf, database))

        if cmd in msgs_conf["pay"]["trigers"]:
            await event.reply(job.pay(user_id, text.split()[2:], msgs_conf, database))

async def main():
    await client.start()
    await client.connect()
    await client.run_until_disconnected()

if __name__ == "__main__":    
    asyncio.run(main())