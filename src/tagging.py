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

from data.database import Database
from data.data_transfer import DataTransfer
from question_answering import QuestionAnswering
from tag_controller import TagController
from display import Display
from help import Help

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
        self.display = Display(self.interface)
        self.help = Help()
        self.contact = self.my_self()

    async def on_message(self, msg: Message):
        """listen message event"""
        #with open("test_message.pkl", 'wb') as fout:
        #    pickle.dump(msg, fout)
        from_contact = msg.talker()
        quoted, text, mention = self.split_quote_and_mention(msg.text())
        room = msg.room()
        to_bot = self.contact.contact_id in msg.payload.mention_ids or\
                 self.contact.contact_id == msg.payload.to_id or\
                 self.contact.name() == mention
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('hey man')
        print(quoted, text, from_contact.get_id(), to_bot)
        if self.tag_controller.handle_msg(quoted, text, from_contact.get_id(), to_bot):
            print('tag controller found reply')
            await conversation.say(self.tag_controller.get_reply())
        elif self.question_answering.handle_msg(text, to_bot):
            print('question answering found reply')
            await conversation.say(self.question_answering.get_reply())
        elif self.display.handle_msg(text, to_bot):
            print('display found reply')
            await conversation.say(self.display.get_reply())
        elif self.help.handle_msg(text, to_bot):
            print('help system found reply')
            await conversation.say(self.help.get_reply())
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
