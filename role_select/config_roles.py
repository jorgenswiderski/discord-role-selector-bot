# config_roles.py

import lightbulb
import hikari
import util
import logging
from lightbulb import BotApp
from config import ConfigManager
from typing import Callable
from .components import create_configure_roles_menu
from .role_selector import update_role_select_message
from .role_directory import update_role_directory_message

logger = logging.getLogger(__name__)
config = ConfigManager("role_select")


async def on_configure_roles(bot: BotApp, event: hikari.InteractionCreateEvent) -> None:
    # Defer the interaction response
    await event.interaction.create_initial_response(
        hikari.ResponseType.DEFERRED_MESSAGE_CREATE,
        flags=hikari.MessageFlag.EPHEMERAL,
    )

    roles = event.interaction.values
    config.guild(event.interaction.guild_id)["roles"] = roles

    await update_role_directory_message(bot, event.interaction.guild_id)
    errors = await update_role_select_message(bot, event.interaction.guild_id)

    if errors:
        await event.interaction.edit_initial_response(
            "\n".join(errors),
        )
        return

    logger.info(
        f"'{util.get_member_str(event.interaction.member)} updated offered roles."
    )

    await event.interaction.edit_initial_response(
        f"The offered roles have been updated.",
    )


def handle_configure_roles(bot: BotApp) -> Callable[[hikari.ShardReadyEvent], None]:
    @lightbulb.add_checks(
        lightbulb.owner_only
        | lightbulb.checks.has_guild_permissions(hikari.Permissions.MANAGE_GUILD)
    )
    @lightbulb.command(
        "configure_roles",
        "Configure which roles will appear in the role select message.",
        ephemeral=True,
    )
    @lightbulb.implements(lightbulb.SlashCommand)
    async def configure_roles(ctx: lightbulb.Context) -> None:
        component = await create_configure_roles_menu(bot, ctx.get_guild())
        await ctx.respond(
            content="Select which roles will appear in the role select message.\n\nNote: Only roles the bot has permission to grant will appear in the list below! If a desired role doesn't appear, make sure it is ordered below this bot's role in the server's role list!",
            component=component,
        )

    return configure_roles
