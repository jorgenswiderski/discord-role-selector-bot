import json
import hikari
from lightbulb import BotApp
from typing import Iterable, Optional, TypeVar, Callable


def copy(obj):
    return json.loads(json.dumps(obj))


def get_member_str(member: hikari.Member):
    return f"'{member.nickname if member.nickname is not None else member.username}' ({member.username}#{member.discriminator})"


T = TypeVar("T")


def find(
    condition: Callable[[T], bool],
    iterable: Iterable[T],
    default_value: Optional[T] = None,
) -> Optional[T]:
    return next((item for item in iterable if condition(item)), default_value)


async def get_message(
    bot: BotApp, id: int, channel_id: int
) -> Optional[hikari.Message]:
    message = bot.cache.get_message(id)

    if message is None:
        try:
            message = await bot.rest.fetch_message(channel_id, id)
        except hikari.NotFoundError:
            return None

    return message
