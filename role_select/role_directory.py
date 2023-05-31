# role_directory.py
import logging

import hikari
from lightbulb import BotApp

import util
from config import ConfigManager

logger = logging.getLogger(__name__)
config = ConfigManager("role_select")


def remove_member_from_config(assigned_roles: dict, member_id: hikari.Snowflake) -> None:
    for members in assigned_roles.values():
        if member_id in members:
            members.remove(member_id)

    logger.info(f"Member '{member_id}' no longer exists, removing from config and directory.")


async def generate_messages_contents(
    bot: BotApp,
    guild_id: hikari.Snowflake,
) -> list[str]:
    _config = config.guild(guild_id)

    if "assigned_roles" not in _config:
        _config["assigned_roles"] = {}

    if "roles" not in _config:
        _config["roles"] = []

    roles = _config["roles"]
    assigned_roles = _config["assigned_roles"]
    message_sections = ["# Current Roles:\n"]

    for role_id in roles:
        member_ids = []

        if role_id in assigned_roles:
            # deep copy, such that the for loop below can remove members from the list without compromising its own iteration
            member_ids = util.copy(assigned_roles[role_id])

        role = bot.cache.get_role(role_id)

        if role is None:
            role = await bot.rest.fetch_role(guild_id, role_id)

        section = f"### {role.mention} ({len(member_ids)})"

        for member_id in member_ids:
            try:
                member = bot.cache.get_member(guild_id, member_id)

                if member is None:
                    member = await bot.rest.fetch_member(guild_id, member_id)

                section += f"\n- {member.mention}"
            except hikari.NotFoundError:
                # user no longer exists
                remove_member_from_config(assigned_roles, member_id)

        message_sections.append(section)

    # Construct sections into message(s), obeying the 2000 character limit
    messages = []
    current_message = message_sections.pop(0)

    for section in message_sections:
        if len(current_message + f"\n{section}") < 2000:
            current_message += f"\n{section}"
        else:
            messages.append(current_message)
            current_message = section

    if current_message:
        messages.append(current_message)

    return messages


async def update_role_directory_message(bot: BotApp, guild_id: hikari.Snowflake) -> bool:
    messages_contents = await generate_messages_contents(bot, guild_id)

    _config = config.guild(guild_id)
    message_config = _config["messages"]
    channels = _config["channels"]

    for channel_id in channels:
        if channel_id not in message_config:
            message_config[channel_id] = {}

        if "role_directory" not in message_config[channel_id]:
            message_config[channel_id]["role_directory"] = []

        # migration from old format
        if isinstance(message_config[channel_id]["role_directory"], int):
            logger.info("Migrating to new role_directory config format.")
            message_config[channel_id]["role_directory"] = [message_config[channel_id]["role_directory"]]

    config_items_to_remove = []
    is_new_messages = False

    for channel_id, channel_messages in message_config.items():
        if "role_directory" in channel_messages:
            message_ids = channel_messages["role_directory"]
            messages = []

            # remove any messages from the config that don't exist
            for message_id in message_ids:
                message = await util.get_message(bot, message_id, channel_id)

                if message is None:
                    message_ids.remove(message_id)
                else:
                    messages.append(message)

            # if we're no longer operating in this channel, delete it all
            if channel_id not in channels:
                for message in messages:
                    await message.delete()

                if len(channel_messages) > 1:
                    channel_messages.pop("role_directory")
                else:
                    config_items_to_remove.append(channel_id)

                continue

            # confirm we have the necessary number of messages
            if len(messages) < len(messages_contents):
                # make more messages
                message = await bot.rest.create_message(int(channel_id), "...")
                message_ids.append(message.id)
                messages.append(message)
                is_new_messages = True

            # delete extra messages, if needed
            while len(messages) > len(messages_contents):
                message = messages.pop()
                await message.delete()
                message_ids.remove(message.id)

            for idx, contents in enumerate(messages_contents):
                await messages[idx].edit(contents)

    for channel_id in config_items_to_remove:
        message_config.pop(channel_id)

    _config.save()

    return is_new_messages


async def update_assigned_roles(bot: BotApp, guild_id: hikari.Snowflake):
    """Update assigned roles from actual guild member roles."""
    _config = config.guild(guild_id)

    if "assigned_roles" not in _config:
        _config["assigned_roles"] = {}

    if "roles" not in _config:
        _config["roles"] = []

    roles = _config["roles"]
    assigned_roles = _config["assigned_roles"]

    """ FIXME: Desync issues with config. If config is updated elsewhere during the execution of this function,
    those changes will likely be overwritten when config is saved here."""

    async for member in bot.rest.fetch_members(guild_id):
        member_roles = await member.fetch_roles()

        for role_id in roles:
            if str(role_id) not in assigned_roles:
                assigned_roles[str(role_id)] = []

            # Check if member has the role
            if any(str(role.id) == role_id for role in member_roles):
                # Add member to role in config if not already there
                if member.id not in assigned_roles[str(role_id)]:
                    logger.info(f"{util.get_member_str(member)} now has role {role_id}.")
                    assigned_roles[str(role_id)].append(member.id)
                    _config.save()
            elif member.id in assigned_roles[str(role_id)]:
                logger.info(f"{util.get_member_str(member)} no longer has role {role_id}.")
                assigned_roles[str(role_id)].remove(member.id)
                _config.save()

    return await update_role_directory_message(bot, guild_id)
