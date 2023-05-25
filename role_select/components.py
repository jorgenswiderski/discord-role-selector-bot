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


def create_configure_roles_menu(bot: BotApp):
    row = bot.rest.build_message_action_row()

    row.add_select_menu(
        components.ComponentType.ROLE_SELECT_MENU,
        "roles_select",
        min_values=1,
        max_values=25,
    )

    return row


def create_role_message(
    bot: BotApp, guild_id: int, config: ConfigState
) -> Optional[dict]:
    if "roles" not in config:
        return

    roles = config["roles"]

    if len(roles) == 0:
        return

    guild = bot.cache.get_guild(guild_id)

    row = bot.rest.build_message_action_row()

    for role_id in roles:
        role = guild.get_role(role_id)

        row.add_interactive_button(
            components.ButtonStyle.PRIMARY,
            f"select_role_{role_id}",
            label=role.name,
        )

    return {
        "content": "If you're focusing on specific content, click here to opt-in to (or out of) a role.\n\nYour name will show up under the corresponding section in the member list so other users may collaborate with you more easily.\n",
        "component": row,
    }
