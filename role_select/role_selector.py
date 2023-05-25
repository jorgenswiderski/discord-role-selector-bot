# role_selector.py

import hikari
import util
import re
import logging
from lightbulb import BotApp
from config import ConfigManager
from .components import create_role_message
from .role_directory import update_role_directory_message

logger = logging.getLogger(__name__)
config = ConfigManager("role_select")


async def toggle_member_role(member: hikari.Member, role: hikari.Role) -> bool:
    """Toggle role on a guild member."""
    roles = await member.fetch_roles()
    _config = config.guild(member.guild_id)

    if "assigned_roles" not in _config:
        _config["assigned_roles"] = {}

    role_data = _config["assigned_roles"]

    if str(role.id) not in role_data:
        role_data[str(role.id)] = []

    if role in roles:
        # If the member already has the role, remove it
        logger.info(
            f"Revoking role '{role.name}' from member {util.get_member_str(member)}."
        )
        await member.remove_role(role)

        try:
            role_data[str(role.id)].remove(member.id)
            _config.save()
        except ValueError:
            pass

        return False
    else:
        # If the member doesn't have the role, add it
        logger.info(
            f"Granting role '{role.name}' to member {util.get_member_str(member)}."
        )
        await member.add_role(role)

        if member.id not in role_data[str(role.id)]:
            role_data[str(role.id)].append(member.id)
            _config.save()

        return True


async def update_role_select_message(bot: BotApp, guild_id: int):
    _config = config.guild(guild_id)

    if "channels" not in _config:
        _config["channels"] = []

    channels = _config["channels"]

    contents = create_role_message(bot, guild_id, _config)

    if contents is None:
        return

    if "messages" not in _config:
        _config["messages"] = {}

    messages = _config["messages"]
    error_channels = set()

    for channel_id, channel_messages in util.copy(messages).items():
        channel_id = str(channel_id)

        try:
            channel = await bot.rest.fetch_channel(channel_id)
        except (hikari.NotFoundError, hikari.ForbiddenError):
            if channel_id in channels:
                error_channels.add(channel_id)
            else:
                messages.pop(channel_id)

            continue

        if "role_selector" in channel_messages:
            message_id = channel_messages["role_selector"]
            message = await channel.fetch_message(message_id)

            if message is not None:
                if channel_id not in channels:
                    await message.delete()

                    if len(messages[channel_id].keys()) == 1:
                        messages.pop(channel_id)
                    else:
                        messages[channel_id].pop("role_selector")
                else:
                    await message.edit(**contents)
            else:
                messages.pop(channel_id)

    for channel_id in channels:
        if channel_id not in messages:
            messages[channel_id] = {}

        if "role_selector" not in messages[channel_id]:
            message = await bot.rest.create_message(channel_id, **contents)
            messages[channel_id]["role_selector"] = message.id

    _config.save()

    errors = []

    for channel_id in error_channels:
        errors.append(
            f"Could not find channel '{channel_id}', check the make sure that channel stills exists and the bot is present in that channel."
        )

    return errors


async def handle_role_interaction(bot: BotApp, event: hikari.InteractionCreateEvent):
    match = re.search(r"\d+$", event.interaction.custom_id)

    if match is None:
        return

    role_id = match.group(0)
    guild_id = event.interaction.guild_id
    guild = bot.cache.get_guild(guild_id)

    role = guild.get_role(role_id) if role_id else None

    if role is not None:
        try:
            status = await toggle_member_role(event.interaction.member, role)

            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content=f"You {'now' if status else 'no longer'} have the role **{role.name}**.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
        except hikari.ForbiddenError:
            await event.interaction.create_initial_response(
                hikari.ResponseType.MESSAGE_CREATE,
                content=f"Failed to grant the requested role.",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

        await update_role_directory_message(bot, event.interaction.guild_id)
