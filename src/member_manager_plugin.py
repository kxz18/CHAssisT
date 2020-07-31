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
from wechaty_puppet import get_logger

from utils.extract_msg import split_quote_and_mention

log = get_logger('Member Mananger Plugin')


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
        self.date = defaultdict(lambda: datetime.now())
        self.thumbsdown = '[弱]'
        self.language = language

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

        if isinstance(conversation, Contact):
            if not to_bot:
                return
            if self.language == 'zh':
                await conversation.say('成员管理功能必须在群聊中使用')
            else:
                await conversation.say('Not work if not in chat room')
            return
        member_count = len(await conversation.member_list())
        # real people >= 4, 3 thumbsdown needed, 3 => 2, 2 => 1
        counts_limit = 3 if member_count > 4 else member_count // 2
        if text.strip() == self.thumbsdown:
            time_delta = datetime.now() - self.date[mention]
            if self.counts[mention] != 0 and time_delta > timedelta(hours=12):
                self.counts[mention] = 0    # former thumbsdown expired
            self.counts[mention] = self.counts[mention] + 1
            self.date[mention] = datetime.now()

            if self.language == 'zh':
                await conversation.say(f'成员{mention}目前已经被踩{self.counts[mention]}次，'
                                       f'被踩{counts_limit}次的成员将被移出群聊')
            else:
                await conversation.say(f'thumbsdown of {mention} is currently {self.counts[mention]}, '
                                       f'member with thumbsdown to {counts_limit} '
                                       'will be removed from chat')
            if self.counts[mention] >= counts_limit:
                removed_contact = Contact.load(msg.payload.mention_ids[0])
                await removed_contact.ready()
                await conversation.delete(removed_contact)
                
                if self.language == 'zh':
                    await conversation.say(f'{removed_contact.name}已被移出群聊')
                else:
                    await conversation.say(f'{removed_contact.name} is removed from chat')
        print(msg.__dict__)

    async def my_self(self) -> Contact:
        """get self contact"""
        my_contact_id = self.bot.contact_id
        contact = Contact.load(my_contact_id)
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
