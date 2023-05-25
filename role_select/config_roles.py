# config_roles.py

import lightbulb
import hikari
from lightbulb import BotApp
from config import ConfigManager
from typing import Callable
from .components import create_configure_roles_menu
from .role_selector import update_role_select_message

config = ConfigManager("role_select")


async def on_configure_roles(bot: BotApp, event: hikari.InteractionCreateEvent) -> None:
    roles = event.interaction.values
    config.guild(event.interaction.guild_id)["roles"] = roles
    errors = await update_role_select_message(bot, event.interaction.guild_id)

    if errors:
        await event.interaction.create_initial_response(
            hikari.ResponseType.MESSAGE_CREATE,
            content="\n".join(errors),
            flags=hikari.MessageFlag.EPHEMERAL,
        )
        return


    await event.interaction.create_initial_response(
        hikari.ResponseType.MESSAGE_CREATE,
        content=f"The offered roles have been updated.",
        flags=hikari.MessageFlag.EPHEMERAL,
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
        await ctx.respond(
            content="Select which roles will appear in the role select message.\n\nMake sure all selected roles are arranged below this bot's role in server settings, otherwise the bot will not be able to assign them!",
            component=create_configure_roles_menu(bot),
        )

    return configure_roles
