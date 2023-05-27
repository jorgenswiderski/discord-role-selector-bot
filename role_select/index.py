# index.py

from typing import Callable

import hikari
import logging
from hikari import Intents
from lightbulb import BotApp
from .role_selector import handle_role_interaction, update_role_select_message
from .config_channels import on_configure_channels, handle_configure_channels
from .config_roles import on_configure_roles, handle_configure_roles
from .role_directory import update_assigned_roles

logger = logging.getLogger(__name__)
ROLE_SELECT_INTENTS = Intents.GUILD_MESSAGES | Intents.GUILD_MESSAGE_REACTIONS


def handle_component_interaction(
    bot: BotApp,
    component_handlers: dict,
) -> Callable[[hikari.InteractionCreateEvent], None]:
    async def on_component_interaction(event: hikari.InteractionCreateEvent) -> None:
        """Handle an interaction create event."""
        if not isinstance(event.interaction, hikari.ComponentInteraction):
            return

        if not hasattr(event.interaction, "custom_id"):
            return

        if event.interaction.custom_id.startswith("select_role_"):
            await handle_role_interaction(bot, event)
            return

        if event.interaction.custom_id.startswith("channel_select_"):
            await on_configure_channels(bot, event)
            return

        if event.interaction.custom_id not in component_handlers:
            logger.error(
                f"No component handler is registered for '{event.interaction.custom_id}'"
            )
            logger.error(event.interaction)
            return

        component_id = event.interaction.custom_id
        handler = component_handlers[component_id]
        await handler(bot, event)

    return on_component_interaction


def handle_on_guild_available(
    bot: BotApp,
) -> Callable[[hikari.GuildAvailableEvent], None]:
    async def on_guild_available(event: hikari.GuildAvailableEvent) -> None:
        logger.info(f"Updating assigned roles for guild {event.guild_id}...")
        is_new_messages = await update_assigned_roles(bot, event.guild_id)

        if is_new_messages:
            await update_role_select_message(bot, event.guild_id, repost=True)

        logger.info(f"Finished updating assigned roles for guild {event.guild_id}.")

    return on_guild_available


def init_role_selector(bot: BotApp) -> None:
    """Register event handlers."""
    bot.listen()(
        handle_component_interaction(
            bot,
            {
                "roles_select": on_configure_roles,
            },
        )
    )

    bot.listen()(handle_on_guild_available(bot))
    bot.command()(handle_configure_channels(bot))
    bot.command()(handle_configure_roles(bot))
