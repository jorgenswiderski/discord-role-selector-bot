# test index.py
import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock
from unittest.mock import patch

from hikari import ComponentInteraction
from hikari import InteractionCreateEvent
from lightbulb import BotApp

from role_select import index


class TestHandleComponentInteraction(IsolatedAsyncioTestCase):
    @patch("role_select.index.handle_role_interaction")
    async def test_handle_role_interaction(self, mock_interaction):
        bot = Mock(spec=BotApp)
        event = Mock(spec=InteractionCreateEvent)
        event.interaction = Mock(spec=ComponentInteraction)
        event.interaction.custom_id = "select_role_test"

        handler = index.handle_component_interaction(bot, {})
        await handler(event)

        mock_interaction.assert_called_once_with(bot, event)

    @patch("role_select.index.on_configure_channels")
    async def test_handle_configure_channels(self, mock_channels):
        bot = Mock(spec=BotApp)
        event = Mock(spec=InteractionCreateEvent)
        event.interaction = Mock(spec=ComponentInteraction)
        event.interaction.custom_id = "channel_select_test"

        handler = index.handle_component_interaction(bot, {})
        await handler(event)

        mock_channels.assert_called_once_with(bot, event)

    @patch("role_select.index.on_configure_roles")
    async def test_handle_configure_roles(self, mock_roles):
        bot = Mock(spec=BotApp)
        event = Mock(spec=InteractionCreateEvent)
        event.interaction = Mock(spec=ComponentInteraction)
        event.interaction.custom_id = "roles_select"

        handler = index.handle_component_interaction(bot, {"roles_select": mock_roles})
        await handler(event)

        mock_roles.assert_called_once_with(bot, event)

    @patch("role_select.index.logger")
    async def test_handle_unknown_interaction(self, mock_logger):
        bot = Mock(spec=BotApp)
        event = Mock(spec=InteractionCreateEvent)
        event.interaction = Mock(spec=ComponentInteraction)
        event.interaction.custom_id = "unknown_interaction"

        handler = index.handle_component_interaction(bot, {})
        await handler(event)

        mock_logger.error.assert_called()  # Check that an error was logged


class TestInitRoleSelector(IsolatedAsyncioTestCase):
    @patch("role_select.index.handle_configure_channels")
    @patch("role_select.index.handle_configure_roles")
    @patch("role_select.index.handle_component_interaction")
    @patch("role_select.index.handle_on_guild_available")
    def test_init_role_selector(self, mock_on_guild, mock_interaction, mock_roles, mock_channels):
        bot = Mock(spec=BotApp)
        mock_listen = Mock()
        mock_command = Mock()

        bot.listen.return_value = mock_listen
        bot.command.return_value = mock_command

        index.init_role_selector(bot)

        # assert listen calls
        bot.listen.assert_any_call()
        self.assertEqual(mock_listen.call_count, 2)

        # assert command calls
        bot.command.assert_any_call()
        self.assertEqual(mock_command.call_count, 2)


if __name__ == "__main__":
    asyncio.run(unittest.main())
