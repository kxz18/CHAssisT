#!/usr/bin/python
# -*- coding:utf-8 -*-
"""plugin of groupchat assistant, including tagging, member manager,
help system and timed task plugin"""
from wechaty.plugin import WechatyPlugin
from wechaty_puppet import get_logger

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
        self.tagging = 
