#!/usr/bin/python
# -*- coding:utf-8 -*-
"""plugin of groupchat assistant, including tagging, member manager,
help system and timed task plugin"""
from wechaty import Wechaty
from wechaty.plugin import WechatyPlugin
from wechaty_puppet import get_logger

from tagging_plugin import Tagging
from timed_task_plugin import TimedTask
from member_manager_plugin import MemberManager
from help_plugin import Help
from help_modules.example_dict import groupchat_bot_help_zh

log = get_logger('Groupchat Assistant')


class GroupchatAssistant(WechatyPlugin):
    """groupchat assistant plugin"""
    @property
    def name(self) -> str:
        """get the name of plugin"""
        return 'groupchat assistant'

    def __init__(self, data_path='database.db', config_path='config.pkl'):
        """params:
            data_path: path of database file,
            config_path: path of database config file, which
                         contains auto-created information"""
        self.plugins = [Tagging(data_path, config_path),
                        TimedTask(),
                        MemberManager(),
                        Help('帮助', '#', groupchat_bot_help_zh)]

    async def init_plugin(self, wechaty: Wechaty):
        """override init_plugin function. Add member plugin to bot"""
        self.bot = wechaty
        self.bot.use(self.plugins)
        for plugin in self.plugins:
            plugin.init_plugin()    # manually initialize their bots
