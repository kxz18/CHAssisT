#!/usr/bin/python
# -*- coding:utf-8 -*-
"""save messages with corresponding tags and answer questions from users,
   display and cleaning function are also provided"""
from typing import Union

from wechaty import Message, Contact, Room
from wechaty.plugin import WechatyPlugin

class Tagging(WechatyPlugin):
    """tagging system plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'tagging'

    async def on_message(self, msg: Message):
        """listen message event"""
        from_contact = msg.talker()
        text = msg.text()
        room = msg.room()
        conversation: Union[
            Room, Contact] = from_contact if room is None else room
        await conversation.ready()
        await conversation.say('hey man')
