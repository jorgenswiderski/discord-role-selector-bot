# main.py
from logger import init_logging

init_logging()

import os  # noqa: E402
import hikari  # noqa: E402
import logging  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from hikari import Intents  # noqa: E402
from lightbulb import BotApp  # noqa: E402
from role_select.index import init_role_selector, ROLE_SELECT_INTENTS  # noqa: E402


logger = logging.getLogger(__name__)

pid = os.getpid()

with open("bot.pid", "w") as f:
    f.write(str(pid))

load_dotenv()  # Load environment variables from .env.
TOKEN = os.getenv("BOT_TOKEN")

# Initialize global intents
INTENTS = Intents.GUILDS

bot = BotApp(
    prefix="!",
    intents=INTENTS | ROLE_SELECT_INTENTS,
    token=TOKEN,
    case_insensitive_prefix_commands=True,
)


@bot.listen()
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    logger.info(f"Logged in as: {bot.get_me()}")


@bot.listen()
async def on_guild_join(event: hikari.GuildJoinEvent) -> None:
    guild_id = event.guild_id
    logger.info(f"Bot joined a new guild: {guild_id}")


@bot.listen()
async def on_guild_leave(event: hikari.GuildLeaveEvent) -> None:
    guild_id = event.guild_id
    logger.info(f"Bot left a guild: {guild_id}")


init_role_selector(bot)

bot.run()
