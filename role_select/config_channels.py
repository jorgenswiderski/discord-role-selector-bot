# config_channels.py
import logging
from typing import Callable

import hikari
import lightbulb
from lightbulb import BotApp

import util
from .components import create_configure_channels_menu
from .role_directory import update_role_directory_message
from .role_selector import update_role_select_message
from config import ConfigManager

logger = logging.getLogger(__name__)
config = ConfigManager("role_select")


async def on_configure_channels(bot: BotApp, event: hikari.InteractionCreateEvent) -> None:
    # Defer the interaction response
    await event.interaction.create_initial_response(
        hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    channels = event.interaction.values
    _config = config.guild(event.interaction.guild_id)
    _config["channels"] = channels

    is_new_messages = await update_role_directory_message(bot, event.interaction.guild_id)
    errors = await update_role_select_message(bot, event.interaction.guild_id, repost=is_new_messages)

    if errors:
        await event.interaction.edit_initial_response(
            content="\n".join(errors),
        )
        return

    message = "Bot is longer operating in any channels."

    if "roles" not in _config or len(_config["roles"]) == 0:
        message = "Bot is will operate in the following channels:"
        for channel_id in channels:
            channel = bot.cache.get_guild_channel(channel_id)
            message += f"\n* #{channel.name}"
        message += "\nHowever, no roles are yet configured. Use `/configure_roles` to initialize roles."
    elif len(channels) > 0:
        message = "Bot is now operating in the following channels:"
        for channel_id in channels:
            channel = bot.cache.get_guild_channel(channel_id)
            message += f"\n* #{channel.name}"

    logger.info(f"{util.get_member_str(event.interaction.member)} changed role select channel to {channel_id}.")

    await event.interaction.edit_initial_response(
        message,
    )


def handle_configure_channels(bot: BotApp) -> Callable[[hikari.ShardReadyEvent], None]:
    @lightbulb.add_checks(lightbulb.owner_only | lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD))
    @lightbulb.command(
        "configure_channels",
        "Configure which channel the role select message will appear in.",
        ephemeral=True,
    )
    @lightbulb.implements(lightbulb.SlashCommand)
    async def configure_channels(ctx: lightbulb.Context) -> None:
        message = "Select a channel for the bot to post its role select message in:"
        comps = create_configure_channels_menu(bot, ctx.guild_id)

        if len(comps) > 1:
            message += (
                "\n\n *Note:* Due to a large amount of channels, the"
                "channels were split into multiple dropdown menus. Please select one."
            )

        await ctx.respond(
            content=message,
            components=comps,
        )

    return configure_channels
