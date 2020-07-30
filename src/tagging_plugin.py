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

from data.database import Database
from data.data_transfer import DataTransfer
from tagging_modules.question_answering import QuestionAnswering
from tagging_modules.tag_controller import TagController
from tagging_modules.display import Display
from utils.extract_msg import split_quote_and_mention

log = get_logger('Tagging plugin')


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

    async def on_message(self, msg: Message):
        """listen message event"""
        self_contact = await self.my_self()
        from_contact = msg.talker()
        log.info('below are dict of message: ')
        log.info(str(msg.__dict__))
        quoted, text, mention = split_quote_and_mention(msg.text())
        log.info('finish spliting')
        log.info(f'quoted: {quoted}, text: {text}, mention: {mention}')
        room = msg.room()
        to_bot = self_contact.get_id() in msg.payload.mention_ids or\
                 self_contact.get_id() == msg.payload.to_id or\
                 self_contact.payload.name == mention
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        log.info(f'finish preprocess, talker: {from_contact.get_id()}, to_bot: {to_bot}')
        try:
            if self.tag_controller.handle_msg(quoted, text, from_contact.get_id(), to_bot):
                log.info('tag controller found reply')
                await conversation.say(self.tag_controller.get_reply())
            elif self.question_answering.handle_msg(text, to_bot):
                log.info('question answering found reply')
                await conversation.say(self.question_answering.get_reply())
            elif self.display.handle_msg(text, to_bot):
                log.info('display found reply')
                await conversation.say(self.display.get_reply())
        except Exception as error:
            log.info(f'something went wrong for tagging plugin: {error}')

    async def my_self(self) -> Contact:
        """get self contact"""
        my_contact_id = self.bot.contact_id
        contact = Contact.load(my_contact_id)
        await contact.ready()
        log.info(f'load self contact: {contact}')
        return contact

    async def on_login(self, contact: Contact):
        """store contact of self"""
        log.info(f'login as {contact}')
        bot_contact = contact
