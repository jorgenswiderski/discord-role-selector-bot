# role_selector.py

import hikari
import util
import re
from lightbulb import BotApp
from config import ConfigManager
from .components import create_role_message

config = ConfigManager("role_select")


async def toggle_member_role(member: hikari.Member, role: hikari.Role) -> bool:
    """Toggle role on a guild member."""
    roles = await member.fetch_roles()

    if role in roles:
        # If the member already has the role, remove it
        print(f"Revoking role '{role.name}' from member '{member.display_name}'")
        await member.remove_role(role)
        return False
    else:
        # If the member doesn't have the role, add it
        print(f"Granting role '{role.name}' to member '{member.display_name}'")
        await member.add_role(role)
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

    for channel_id, message_id in util.copy(messages).items():
        channel_id = str(channel_id)

        try:
            channel = await bot.rest.fetch_channel(channel_id)
        except (hikari.NotFoundError, hikari.ForbiddenError):
            if channel_id in channels:
                error_channels.add(channel_id)
            else:
                messages.pop(channel_id)

            continue

        message = await channel.fetch_message(message_id)

        if message is not None:
            if channel_id not in channels:
                await message.delete()
                messages.pop(channel_id)
            else:
                await message.edit(**contents)
        else:
            messages.pop(channel_id)

    for channel_id in channels:
        if channel_id not in messages:
            channel = bot.cache.get_guild_channel(channel_id)

            if channel is None:
                messages.pop(channel_id)
                continue

            sent_message = await channel.send(**contents)
            messages[channel_id] = sent_message.id

    _config.save()

    errors = []

    for channel_id in error_channels:
        errors.append(f"Could not find channel '{channel_id}', check the make sure that channel stills exists and the bot is present in that channel.")

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
        status = await toggle_member_role(event.interaction.member, role)

        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            content=f"You {'now' if status else 'no longer'} have the role **{role.name}**.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )
