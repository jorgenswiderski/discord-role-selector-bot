# components.py

from typing import Optional

import hikari
from lightbulb import BotApp
from hikari import components
from config import ConfigState


# Utility methods for role selection
def create_configure_channels_menu(bot: BotApp):
    row = bot.rest.build_message_action_row()
    row.add_channel_menu(
        "channel_select",
        channel_types=[hikari.ChannelType.GUILD_TEXT],
        min_values=0,
        max_values=1,
    )

    return row


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
        "content": "If you're focusing on specific content, click here to opt-in to a role.\n\nYour name will show up under the corresponding section in the member list so other users may collaborate with you more easily.\n",
        "component": row,
    }
