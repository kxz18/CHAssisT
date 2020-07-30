#!/usr/bin/python
# -*- coding:utf-8 -*-
"""save messages with corresponding tags and answer questions from users,
   display and cleaning function are also provided"""
import re
from typing import Union
import pickle

from wechaty import Message, Contact, Room
from wechaty.plugin import WechatyPlugin
from wechaty_puppet import get_logger

from timed_task_modules.task_controller import TaskController
from utils.extract_msg import split_quote_and_mention

log = get_logger('Timed Task Plugin')


class TimedTask(WechatyPlugin):
    """tagging system plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'timed task'

    def __init__(self):
        """doc"""
        self.task_controller = TaskController()

    async def on_message(self, msg: Message):
        """listen message event"""
        self_contact = await self.my_self()
        from_contact = msg.talker()
        quoted, text, mention = split_quote_and_mention(msg.text())
        room = msg.room()
        to_bot = self_contact.get_id() in msg.payload.mention_ids or\
                 self_contact.get_id() == msg.payload.to_id or\
                 self_contact.payload.name == mention
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        try:
            if self.task_controller.handle_msg(text, conversation, to_bot):
                print('task controller found reply')
                await conversation.say(self.task_controller.get_reply())
        except Exception as error:
            print(f'something went wrong for timed task plugin: {error}')

    async def my_self(self) -> Contact:
        """get self contact"""
        my_contact_id = self.bot.contact_id
        contact = Contact.load(my_contact_id)
        await contact.ready()
        return contact
