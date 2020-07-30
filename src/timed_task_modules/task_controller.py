#!/usr/bin/python
# -*- coding:utf-8 -*-
"""handle commands of timed task"""
import re
from typing import Union
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from wechaty import Contact
from wechaty.user import Room
from timed_task_modules import reply

KEY_TIMED_TASK = '定时消息'
# KEY_TIMED_TASK = 'timed message'
KEY_SPLIT = r'#'


class TaskController:
    """handle commands of "creating timed task"""
    def __init__(self):
        """attributes:
            scheduler: job scheduler
            reply: reply to user command"""
        self.reply = ''  # during handling, help or reply messages may be needed
        self.scheduler = AsyncIOScheduler()
        self.id_count = 0
        self.scheduler.start()

    def handle_msg(self, msg, conversation: Union[Contact, Room], to_bot):
        """handle commands
        params:
            msg: str, messages from talker
            sayer: the place to say the words
            to_bot: bool, whether talking to the bot
            """
        # clear reply
        self.reply = ''
        # check if saying to the bot
        if not to_bot:
            return False
        if self.handle_create_task(msg, conversation):
            return True
        return False

    def get_reply(self):
        """return reply"""
        return self.reply

    def handle_create_task(self, msg: str, conversation: Union[Contact, Room]):
        """handle create task command"""
        if self.date_type_task(msg, conversation):
            return True
        if self.cron_type_task(msg, conversation):
            return True
        return False

    def date_type_task(self, msg: str, conversation: Union[Contact, Room]):
        """parse date type timed task
        pattern is like: timed message#y-m-d h:min:sec-msg"""
        pattern = re.compile(r'^\s*' + KEY_TIMED_TASK + r'\s*' + KEY_SPLIT
                             + r'\s*(\d+-\d+-\d+\s+\d+:\d+:.*?)-(.*?)$')
        msg = re.sub(r'\s+', ' ', msg)
        msg = re.sub('：', ':', msg)
        res = pattern.match(msg)
        if res is None:
            return False
        self.id_count += 1
        self.scheduler.add_job(conversation.say, 'date', run_date=res.group(1),
                               args=[res.group(2)], id=str(self.id_count))
        self.reply = reply.set_date_timed_task_success(res.group(1), res.group(2))
        return True

    def cron_type_task(self, msg: str, conversation: Union[Contact, Room]):
        """parse cron type timed task
        pattern is like 'timed message#y-m-d-dof-h-min-msg"""
        pattern = re.compile(r'^\s*' + KEY_TIMED_TASK + r'\s*' + KEY_SPLIT
                             + r'\s*' + '-'.join([r'(\d+|\*)' for _ in range(6)])
                             + '-' + r'(.*?)$')
        res = pattern.match(msg)
        if res is None:
            return False
        params = {}
        for idx, key in enumerate(['year', 'month', 'day', 'week day', 'hour', 'minute']):
            params[key] = res.group(idx + 1)
        self.id_count += 1
        self.scheduler.add_job(conversation.say, 'cron',
                               year=params['year'], month=params['month'],
                               day=params['day'], day_of_week=params['week day'],
                               hour=params['hour'], minute=params['minute'],
                               args=[res.group(7)],
                               id=str(self.id_count))
        self.reply = reply.set_cron_timed_task_success(params, res.group(7))
        return True
