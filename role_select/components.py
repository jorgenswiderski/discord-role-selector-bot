# components.py

from typing import Optional

import hikari
from lightbulb import BotApp
from hikari import components
from config import ConfigState


def create_configure_channels_menu(bot: BotApp, guild_id: int):
    channel_view = bot.cache.get_guild_channels_view()
    channels = []

    for channel_id in channel_view:
        channel = bot.cache.get_guild_channel(channel_id)

        if channel.guild_id == guild_id:
            channels.append(channel)

    comp = []

    for i in range(0, len(channels), 15):
        row = bot.rest.build_message_action_row()
        menu = row.add_text_menu(
            f"channel_select_{i}",
        )

        for channel in channels[i : i + 15]:
            menu.add_option(channel.name, str(channel.id))

        comp.append(row)

    return comp


async def create_configure_roles_menu(bot: BotApp, guild: hikari.Guild):
    bot_member = guild.get_my_member()
    bot_roles = bot_member.get_roles()
    bot_role = next(
        (
            role
            for role in bot_roles
            if hasattr(role, "bot_id") and role.bot_id == bot_member.id
        )
    )

    roles = []
    guild_roles = await guild.fetch_roles()

    for role in guild_roles:
        if role.name == "@everyone":
            continue

        if role.position < bot_role.position:
            roles.append(role)

    row = bot.rest.build_message_action_row()

    menu = row.add_text_menu(
        "roles_select",
        min_values=1,
        max_values=len(roles),
    )

    for role in roles:
        menu.add_option(role.name, str(role.id))

    return row


def create_role_message(
    bot: BotApp, guild_id: int, config: ConfigState
) -> Optional[dict]:
    if "roles" not in config:
        return None

    role_ids = config["roles"]

    if len(role_ids) == 0:
        return None

    guild = bot.cache.get_guild(guild_id)
    roles = list(map(lambda role_id: guild.get_role(role_id), role_ids))
    roles.sort(key=lambda role: len(role.name))

    action_rows = []
    current_row = bot.rest.build_message_action_row()
    longest = True

    while roles:
        role = roles.pop(-1 if longest else 0)
        longest = not longest

        current_row.add_interactive_button(
            components.ButtonStyle.PRIMARY,
            f"select_role_{role.id}",
            label=role.name,
        )

        if len(current_row.components) >= 5:
            action_rows.append(current_row)
            current_row = bot.rest.build_message_action_row()

    # Add the remaining components to the last action row
    if len(current_row.components) > 0:
        action_rows.append(current_row)

    return {
        "content": "If you're focusing on specific content, click here to opt-in to (or out of) a role.\n\nYour name will show up under the corresponding section in the member list so other users may collaborate with you more easily.\n",
        "components": action_rows,
    }
