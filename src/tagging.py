#!/usr/bin/python
# -*- coding:utf-8 -*-
"""save messages with corresponding tags and answer questions from users,
   display and cleaning function are also provided"""
from typing import Union

from wechaty import Message, Contact, Room
from wechaty.plugin import WechatyPlugin

from data.database import Database
from data.data_transfer import DataTransfer
from question_answering import QuestionAnswering
from tag_controller import TagController

class Tagging(WechatyPlugin):
    """tagging system plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'tagging'

    def __init__(self, data_path='database.db', config_path='config.pkl'):
        """params:
            data_path: path of database file,
            config_path: path of database config file, which
                         contains auto-created information"""
        self.data_path = data_path
        self.config_path = config_path
        self.interface = DataTransfer(Database(data_path, config_path))
        self.question_answering = QuestionAnswering(self.interface)
        self.tag_controller = TagController(self.interface)

    async def on_message(self, msg: Message):
        """listen message event"""
        from_contact = msg.talker()
        text = msg.text()
        room = msg.room()
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('hey man')
        print(msg.__dict__)
