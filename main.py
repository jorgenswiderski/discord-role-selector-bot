# main.py

import os
import hikari
from dotenv import load_dotenv
from hikari import Intents
from lightbulb import BotApp

from role_select.index import init_role_selector, ROLE_SELECT_INTENTS

load_dotenv()  # Load environment variables from .env.
TOKEN = os.getenv("BOT_TOKEN")

INTENTS = Intents.GUILDS

bot = BotApp(
    prefix="!",
    intents=INTENTS | ROLE_SELECT_INTENTS,
    token=TOKEN,
    case_insensitive_prefix_commands=True,
)


@bot.listen()
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    print(f"Logged in as: {bot.get_me()}")


@bot.listen()
async def on_guild_join(event: hikari.GuildJoinEvent) -> None:
    guild_id = event.guild_id
    print(f"Bot joined a new guild: {guild_id}")


@bot.listen()
async def on_guild_leave(event: hikari.GuildLeaveEvent) -> None:
    guild_id = event.guild_id
    print(f"Bot left a guild: {guild_id}")


init_role_selector(bot)

bot.run()
