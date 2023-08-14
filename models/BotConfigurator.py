import os
import yaml
import sys
import asyncio
import threading
import pydash as _

from lib.func import get_logger
from telegram import (Bot,
                      ReplyKeyboardMarkup,
                      KeyboardButton,
                      ReplyKeyboardRemove,
                      InlineKeyboardMarkup,
                      InlineKeyboardButton)

from lib.constants import CONFIG_FILE

log = get_logger("BotConfigurator")


class BotConfigurator():

    def __init__(self, config_file: str = CONFIG_FILE, update_config_file: bool = True) -> None:
        self.config_file = config_file
        self.update_config_file = update_config_file
        self.commands = None
        self._config = None

    @property
    def config(self) -> dict:
        if self._config:
            return self._config
        if not os.path.isfile(self.config_file):
            log.critical(f"Configuration file {self.config_file} not found.")
            sys.exit(1)
        with open(self.config_file, 'r') as config_file:
            self._config = yaml.load(config_file, Loader=yaml.FullLoader)
        return self._config

    def set(self, path, value) -> None:
        _.set_(self._config, path, value)
        if self.update_config_file:
            self.save_config()

    def save_config(self) -> None:
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config, f)

    def validate(self) -> bool:
        failed_checks = []
        if not _.has(self.config, 'bot.token'):
            failed_checks.append("You must pass the token you received from https://t.me/Botfather!")
        if not (_.has(self.config, 'transmission.host') and \
                _.has(self.config, 'transmission.port') and \
                _.has(self.config, 'transmission.user') and \
                _.has(self.config, 'transmission.password')):
            failed_checks.append(
                "Provide transmission configuration options: host, user, password")
        if failed_checks:
            for check in failed_checks:
                log.critical(check)
            return False
        return True

    def get_actions_keyboard(self, actions):
        if actions:
            return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=str(key)) for key in actions]],
                                       resize_keyboard=True)
        return ReplyKeyboardRemove()

    def get_downloads_keyboard(self):
        # Download directories
        # Transmission server needs write access to these directories
        return InlineKeyboardMarkup(
            [[InlineKeyboardButton(key.capitalize(), callback_data=value) for key, value in dict(self.config['directories']).items()]])

    def set_bot_commands(self, commands):
        self.commands = commands
        _thread = threading.Thread(target=self._between_callback)
        _thread.start()

    def add_user(self, id):
        if id not in self._config['bot']['allowed_users']:
            self._config['bot']['allowed_users'].append(id)
            self.save_config()

    def _between_callback(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self._set_bot_commands())
        loop.close()

    async def _set_bot_commands(self):
        await Bot(token=self.config['bot']['token']).set_my_commands(self.commands)
        log.info("Commands updated")
