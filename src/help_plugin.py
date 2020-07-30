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
from wechaty_puppet import get_logger

from help_modules.help import Help
from utils.extract_msg import split_quote_and_mention

log = get_logger('Tagging plugin')


class HelpSystem(WechatyPlugin):
    """tagging system plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'help system'

    def __init__(self, key_help, key_split, help_dict):
        """params:
            key_help: keyword of help
            key_split: signal of dividing help keywords and other content
            help_dict: content of help"""
        self.help = Help(key_help, key_split, help_dict)

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
            if self.help.handle_msg(text, to_bot):
                log.info('help system found reply')
                await conversation.say(self.help.get_reply())
        except Exception as error:
            log.info(f'something went wrong for help system plugin: {error}')

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
