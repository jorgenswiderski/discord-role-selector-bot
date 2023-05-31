# discord-role-selector

A simple discord bot with two main features:
  * Users can opt in or out of roles by clicking buttons, as configured by the server manager.
  * A list of users, by role, is maintained automatically such that users can easily collaborate with other users (even if those users are offline).

Built using python3 with `hikari` and `hikari-lightbulb` for Discord integration. Additionally, CI/CD is managed by by Github Actions, and git hooks are implemented using `pre-commit` for linting, formatting, unit testing and more.
