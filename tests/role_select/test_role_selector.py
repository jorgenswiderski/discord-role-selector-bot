# test_role_selector.py

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import hikari
from role_select.role_selector import (
    toggle_member_role,
    update_role_select_message,
    handle_role_interaction,
)
from lightbulb import BotApp


class TestToggleMemberRole(IsolatedAsyncioTestCase):
    @patch("role_select.role_selector.config")
    async def test_toggle_member_role(self, mock_config):
        mock_member = Mock(spec=hikari.Member)
        mock_role = Mock(spec=hikari.Role)
        _config_mock = MagicMock()
        _config_mock.save.return_value = None
        mock_config.guild.return_value = _config_mock
        _config_mock.__getitem__.return_value = {
            "assigned_roles": {str(mock_role.id): []}
        }

        # Test the case where the role is already assigned, it should be removed
        mock_member.fetch_roles.return_value = [mock_role]
        status = await toggle_member_role(mock_member, mock_role)
        self.assertFalse(status)
        mock_member.add_role.assert_not_called()
        mock_member.remove_role.assert_called_once_with(mock_role)
        mock_member.reset_mock()
        mock_role.reset_mock()

        # Test the case where the role is not assigned, it should be added
        mock_member.fetch_roles.return_value = []
        status = await toggle_member_role(mock_member, mock_role)
        self.assertTrue(status)
        mock_member.add_role.assert_called_once_with(mock_role)
        mock_member.remove_role.assert_not_called()


class TestUpdateRoleSelectMessage(IsolatedAsyncioTestCase):
    @patch("role_select.role_selector.config")
    @patch("role_select.role_selector.util")
    @patch("role_select.role_selector.create_role_message")
    async def test_update_role_select_message(
        self, mock_create_role_message, mock_util, mock_config
    ):
        bot = AsyncMock(spec=BotApp)
        bot.rest.create_message = AsyncMock()
        mock_util.copy.return_value = {}
        _config_mock = MagicMock()
        _config_mock.save.return_value = None
        mock_config.guild.return_value = _config_mock
        guild_id = 12345
        mock_create_role_message.return_value = {
            "contents": "Role message contents",
            "components": MagicMock(),
        }
        mock_util.copy.side_effect = lambda x: x
        bot.rest.fetch_channel = AsyncMock()
        mock_channel = MagicMock(spec=hikari.TextableChannel)
        bot.rest.fetch_channel.return_value = mock_channel
        mock_message = MagicMock(spec=hikari.Message)
        mock_channel.fetch_message.return_value = mock_message

        # Test case where message is created
        _config_mock.__getitem__.side_effect = lambda key: {
            "channels": ["1234567890"],
            "messages": {"1234567890": {"role_directory": 234567890}},
        }[key]
        errors = await update_role_select_message(bot, guild_id)
        bot.rest.fetch_channel.assert_called_with("1234567890")
        mock_channel.fetch_message.assert_not_called()
        mock_message.edit.assert_not_called()
        mock_message.delete.assert_not_called()
        bot.rest.create_message.assert_called_once()
        self.assertEqual(errors, [])
        bot.reset_mock()

        # Test case where message is updated
        _config_mock.__getitem__.side_effect = lambda key: {
            "channels": ["1234567890"],
            "messages": {
                "1234567890": {"role_selector": 123456789, "role_directory": 234567890}
            },
        }[key]
        errors = await update_role_select_message(bot, guild_id)
        bot.rest.fetch_channel.assert_called_with("1234567890")
        mock_channel.fetch_message.assert_called_with(123456789)
        mock_message.edit.assert_called_once()
        mock_message.delete.assert_not_called()
        bot.rest.create_message.assert_not_called()
        self.assertEqual(errors, [])
        mock_message.reset_mock()

        # Test case where message is deleted
        _config_mock.__getitem__.side_effect = lambda key: {
            "channels": [],
            "messages": {
                "1234567890": {"role_selector": 123456789, "role_directory": 234567890}
            },
        }[key]
        errors = await update_role_select_message(bot, guild_id)
        bot.rest.fetch_channel.assert_called_with("1234567890")
        mock_channel.fetch_message.assert_called_with(123456789)
        mock_message.edit.assert_not_called()
        mock_message.delete.assert_called_once()
        bot.rest.create_message.assert_not_called()
        self.assertEqual(errors, [])
        mock_message.reset_mock()

        # Test when channel cannot be found
        _config_mock.__getitem__.side_effect = lambda key: {
            "channels": ["invalid_channel"],
            "messages": {"invalid_channel": {"role_selector": 123456789}},
        }[key]
        bot.rest.fetch_channel.side_effect = hikari.NotFoundError(
            "Channel not found", "url", "headers", "raw_body"
        )
        errors = await update_role_select_message(bot, guild_id)
        bot.rest.fetch_channel.assert_called_with("invalid_channel")
        mock_message.edit.assert_not_called()
        mock_message.delete.assert_not_called()
        bot.rest.create_message.assert_not_called()
        self.assertNotEqual(errors, [])  # ensure errors list is not empty


class TestHandleRoleInteraction(IsolatedAsyncioTestCase):
    @patch("role_select.role_selector.toggle_member_role")
    @patch("role_select.role_selector.update_role_directory_message")
    async def test_handle_role_interaction(self, mock_update_message, mock_toggle_role):
        bot = Mock(spec=BotApp)
        event = AsyncMock(spec=hikari.InteractionCreateEvent)
        event.interaction.create_initial_response = AsyncMock()
        mock_guild = Mock(spec=hikari.Guild)
        mock_role = Mock(spec=hikari.Role)
        event.interaction.guild_id = 12345
        event.interaction.custom_id = "select_role_12345"
        bot.cache.get_guild.return_value = mock_guild
        mock_guild.get_role.return_value = mock_role
        mock_toggle_role.return_value = True

        # Test the case where role is successfully granted
        await handle_role_interaction(bot, event)
        event.interaction.create_initial_response.assert_called_once()

        # Test the case where role granting failed
        mock_toggle_role.side_effect = hikari.ForbiddenError(
            "url", "headers", "raw_body"
        )
        await handle_role_interaction(bot, event)
        event.interaction.create_initial_response.assert_called_with(
            hikari.ResponseType.MESSAGE_CREATE,
            content=f"Failed to grant the requested role.",
            flags=hikari.MessageFlag.EPHEMERAL,
        )


if __name__ == "__main__":
    unittest.main()
