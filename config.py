# config.py

import json
import util

try:
    with open("config.json") as f:
        config = json.load(f)
except:
    config = {}


def save_config():
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)


class ConfigState(dict):
    def __init__(self, module: str, guild_id: int):
        self.module = module
        guild_id = str(guild_id)
        self.guild_id = guild_id

        if not guild_id in config:
            config[guild_id] = {}

        if not module in config[guild_id]:
            config[guild_id][module] = {}

        self.update(config[guild_id][module])

    def __setitem__(self, __key: any, __value: any) -> None:
        value = super().__setitem__(__key, __value)
        config[self.guild_id][self.module][__key] = __value
        save_config()

        return value

    def save(self):
        config[self.guild_id][self.module] = util.copy(self)
        save_config()


class ConfigManager:
    def __init__(self, module: str):
        self.module = module

    def guild(self, id: int) -> ConfigState:
        return ConfigState(self.module, id)
