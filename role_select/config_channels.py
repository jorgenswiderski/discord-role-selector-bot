# config_channels.py

import lightbulb
import hikari
import util
from lightbulb import BotApp
from config import ConfigManager
from typing import Callable
from .components import create_configure_channels_menu
from .role_selector import update_role_select_message

config = ConfigManager("role_select")


async def on_configure_channels(
    bot: BotApp, event: hikari.InteractionCreateEvent
) -> None:
    channels = event.interaction.values
    _config = config.guild(event.interaction.guild_id)
    _config["channels"] = channels

    errors = await update_role_select_message(bot, event.interaction.guild_id)

    if errors:
        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            content="\n".join(errors),
            flags=hikari.MessageFlag.EPHEMERAL,
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

    print(f"{util.get_member_str(event.interaction.member)} changed role select channel to {channel_id}.")

    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        content=message,
        flags=hikari.MessageFlag.EPHEMERAL,
    )


def handle_configure_channels(bot: BotApp) -> Callable[[hikari.ShardReadyEvent], None]:
    @lightbulb.add_checks(
        lightbulb.owner_only
        | lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    )
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
            message += "\n\n *Note:* Due to a large amount of channels, the channels were split into multiple dropdown menus. Please select one."

        await ctx.respond(
            content=message,
            components=comps,
        )

    return configure_channels
