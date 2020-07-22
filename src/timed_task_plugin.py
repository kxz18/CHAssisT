#!/usr/bin/python
# -*- coding:utf-8 -*-
"""save messages with corresponding tags and answer questions from users,
   display and cleaning function are also provided"""
import re
from typing import Union
import pickle

from wechaty import Message, Contact, Room
from wechaty.plugin import WechatyPlugin
from wechaty.user.contact_self import ContactSelf

from timed_task_modules.task_controller import TaskController

class TimedTask(WechatyPlugin):
    """tagging system plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'timed task'

    def __init__(self):
        """params:
            data_path: path of database file,
            config_path: path of database config file, which
                         contains auto-created information"""
        self.task_controller = TaskController()

    async def on_message(self, msg: Message):
        """listen message event"""
        self_contact = await self.my_self()
        from_contact = msg.talker()
        quoted, text, mention = self.split_quote_and_mention(msg.text())
        room = msg.room()
        to_bot = self_contact.contact_id in msg.payload.mention_ids or\
                 self_contact.contact_id == msg.payload.to_id or\
                 self_contact.name() == mention
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('hey man')
        print(quoted, text, from_contact.get_id(), to_bot)
        if self.task_controller.handle_msg(text, conversation, to_bot):
            print('task controller found reply')
            await conversation.say(self.task_controller.get_reply())
        print(msg.__dict__)

    async def my_self(self) -> ContactSelf:
        """get self contact"""
        my_contact_id = self.bot.puppet.self_id()
        contact = self.ContactSelf.load(my_contact_id)
        await contact.ready()
        return contact

    @classmethod
    def split_quote_and_mention(cls, text):
        """split quoted text, reply text and mention"""
        quoted, text_and_mention = cls.split_quote(text)
        reply, mention = cls.split_mention(text_and_mention)
        return (quoted, reply, mention)

    @classmethod
    def split_quote(cls, text):
        """split quoted text and reply from given text,
        the pattern is like "talker: quoted"\n(several -)\nreply"""
        pattern = re.compile(r'\"(.*?)\"\n' +
                             ' '.join(['-' for _ in range(15)]) +
                             r'\n(.*?)$')
        res = pattern.match(text)
        if res is None:
            return (None, text)
        return (res.group(1), res.group(2))

    @classmethod
    def split_mention(cls, text):
        """split @sb from given text,
        pattern is like: text @alias\u2005"""
        pattern = re.compile(r'(.*?)\s+(.*?)\u\d+$')
        res = pattern.match(text)
        if res is None:
            return (text, None)
        return (res.group(1), res.group(2))
