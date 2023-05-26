# role_directory.py

import hikari
import logging
import util
from lightbulb import BotApp
from config import ConfigManager
from typing import Callable

logger = logging.getLogger(__name__)
config = ConfigManager("role_select")


async def generate_message_contents(
    bot: BotApp,
    guild_id: hikari.Snowflake,
):
    _config = config.guild(guild_id)

    if "assigned_roles" not in _config:
        _config["assigned_roles"] = {}

    if "roles" not in _config:
        _config["roles"] = []

    roles = _config["roles"]
    assigned_roles = _config["assigned_roles"]
    message_contents = "# Current Roles:\n\n"

    for role_id in roles:
        member_ids = []

        if role_id in assigned_roles:
            member_ids = assigned_roles[role_id]

        role = bot.cache.get_role(role_id)

        if role is None:
            role = await bot.rest.fetch_role(guild_id, role_id)

        message_contents += f"### {role.mention} ({len(member_ids)})"

        for member_id in member_ids:
            member = bot.cache.get_member(guild_id, member_id)

            if member is None:
                member = await bot.rest.fetch_member(guild_id, member_id)

            message_contents += f"\n- {member.mention}"

        message_contents += "\n"

    return message_contents


async def update_role_directory_message(bot: BotApp, guild_id: hikari.Snowflake):
    message_contents = await generate_message_contents(bot, guild_id)

    _config = config.guild(guild_id)
    messages = _config["messages"]
    channels = _config["channels"]

    for channel_id, channel_messages in util.copy(messages).items():
        if "role_directory" in channel_messages:
            message_id = channel_messages["role_directory"]
            message = bot.cache.get_message(message_id)

            if message is None:
                message = await bot.rest.fetch_message(channel_id, message_id)

            if message is None:
                logger.warning(
                    f"Could not find role directory with message id '{message_id}', deleting from config."
                )
                channel_messages.pop("role_directory")
            elif channel_id not in channels:
                await message.delete()

                if len(messages[channel_id].keys()) == 1:
                    messages.pop(channel_id)
                else:
                    messages[channel_id].pop("role_directory")

            else:
                await message.edit(message_contents)

    for channel_id in channels:
        if channel_id not in messages:
            messages[channel_id] = {}

        if "role_directory" not in messages[channel_id]:
            message = await bot.rest.create_message(int(channel_id), message_contents)
            messages[channel_id]["role_directory"] = message.id

    _config.save()


async def update_assigned_roles(bot: BotApp, guild_id: hikari.Snowflake):
    """Update assigned roles from actual guild member roles."""
    _config = config.guild(guild_id)

    if "assigned_roles" not in _config:
        _config["assigned_roles"] = {}

    if "roles" not in _config:
        _config["roles"] = []

    roles = _config["roles"]
    assigned_roles = _config["assigned_roles"]

    # FIXME: Desync issues with config. If config is updated elsewhere during the execution of this function, those changes will likely be overwritten when config is saved here.

    async for member in bot.rest.fetch_members(guild_id):
        member_roles = await member.fetch_roles()

        for role_id in roles:
            if str(role_id) not in assigned_roles:
                assigned_roles[str(role_id)] = []

            # Check if member has the role
            if any(str(role.id) == role_id for role in member_roles):
                # Add member to role in config if not already there
                if member.id not in assigned_roles[str(role_id)]:
                    logger.info(
                        f"{util.get_member_str(member)} now has role {role_id}."
                    )
                    assigned_roles[str(role_id)].append(member.id)
                    _config.save()
            elif member.id in assigned_roles[str(role_id)]:
                logger.info(
                    f"{util.get_member_str(member)} no longer has role {role_id}."
                )
                assigned_roles[str(role_id)].remove(member.id)
                _config.save()

    await update_role_directory_message(bot, guild_id)


def handle_on_guild_available(
    bot: BotApp,
) -> Callable[[hikari.GuildAvailableEvent], None]:
    async def on_guild_available(event: hikari.GuildAvailableEvent) -> None:
        logger.info(f"Updating assigned roles for guild {event.guild_id}...")
        await update_assigned_roles(bot, event.guild_id)
        logger.info(f"Finished updating assigned roles for guild {event.guild_id}.")

    return on_guild_available
