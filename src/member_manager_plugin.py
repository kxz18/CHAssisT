#!/usr/bin/python
# -*- coding:utf-8 -*-
"""save messages with corresponding tags and answer questions from users,
   display and cleaning function are also provided"""
import re
from typing import Union, List
from collections import defaultdict
from datetime import datetime, timedelta

from wechaty import Message, Contact, Room
from wechaty.plugin import WechatyPlugin
from wechaty.user.contact_self import ContactSelf

class MemberManager(WechatyPlugin):
    """member manager plugin for bot"""
    @property
    def name(self) -> str:
        """get the name of the plugin"""
        return 'member manager'

    def __init__(self, language='zh'):
        """attributes:
        counts: counts of thumbsdown of certain person
        reason: date when somebody last receive thumbsdown
        language: en for English, zh for Chinese"""
        self.counts = defaultdict(int)
        self.date = defaultdict(datetime)
        self.thumbsdown = '[thumbsdown]'
        self.language = language

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
        print(quoted, text, from_contact.get_id(), to_bot)

        if isinstance(conversation, Contact):
            if self.language == 'zh':
                await conversation.say('成员管理功能必须在群聊中使用')
            else:
                await conversation.say('Not work if not in chat room')
            return

        counts_limit = 3 if len(await conversation.member_list()) > 4 else 2
        if text == self.thumbsdown:
            time_delta = datetime.now() - self.date[mention]
            if self.counts[mention] != 0 and time_delta > timedelta(hours=12):
                self.counts[mention] = 0    # former thumbsdown expired
            self.counts[mention] = self.counts[mention] + 1

            if self.language == 'zh':
                await conversation.say(f'成员{mention}目前已经被踩{self.counts[mention]}次，'
                                       f'被踩{counts_limit}次的成员将被移出群聊')
            else:
                await conversation.say(f'thumbsdown of {mention} is currently {self.counts[mention]}, '
                                       f'member with thumbsdown to {counts_limit} '
                                       'will be removed from chat')
            if self.counts[mention] >= counts_limit:
                removed_contact = Contact.load(mention)
                conversation.delete(removed_contact)
                
                if self.language == 'zh':
                    await conversation.say(f'{removed_contact.name()}已被移出群聊')
                else:
                    await conversation.say(f'{removed_contact.name()} is removed from chat')
        print(msg.__dict__)

    async def my_self(self) -> ContactSelf:
        """get self contact"""
        my_contact_id = self.bot.puppet.self_id()
        contact = ContactSelf.load(my_contact_id)
        await contact.ready()
        return contact

    async def on_room_join(self, room: Room, invitees: List[Contact],
                           inviter: Contact, date: datetime):
        """called when somebody was invited to the group chat"""
        await room.ready()
        if self.language == 'zh':
            await room.say(f'{"、".join([contact.name() for contact in invitees])} '
                           '加入了我们的群聊，欢迎！')

        else:
            await room.say(f'{",".join([contact.name() for contact in invitees])} '
                           f'{"has" if len(invitees) == 1 else "have"} '
                           f'joined, welcome !')

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
