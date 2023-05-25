# role_directory.py

import hikari
import logging
from lightbulb import BotApp
from config import ConfigManager

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

    for channel_id, channel_messages in messages.items():
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
            else:
                await message.edit(message_contents)

        if "role_directory" not in channel_messages:
            message = await bot.rest.create_message(channel_id, message_contents)
            channel_messages["role_directory"] = message.id

    _config.save()
