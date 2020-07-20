#!/usr/bin/python
# -*- coding:utf-8 -*-
"""handle commands of timed task"""
import re
from typing import Union
from apscheduler.schedulers.background import BackgroundScheduler
from wechaty import Contact
from wechaty.user import Room
from timed_task_modules import reply

KEY_TIMED_TASK = 'timed message'
KEY_SPLIT = r'#'


class TaskController:
    """handle commands of "creating timed task"""
    def __init__(self):
        """attributes:
            scheduler: job scheduler
            reply: reply to user command"""
        self.reply = ''  # during handling, help or reply messages may be needed
        self.scheduler = BackgroundScheduler()
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

    def get_reply(self):
        """return reply"""
        return self.reply

    def handle_create_task(self, msg: str, conversation: Union[Contact, Room]):
        """generate timed task"""
        # pattern is like 'timed message#y-m-d-dof-h-min-x'
        # data which are x days before will be deleted
        pattern = re.compile(r'^' + KEY_TIMED_TASK + KEY_SPLIT
                             + '-'.join([r'(\d+|\*)' for _ in range(6)])
                             + '-' + r'.*?$')
        res = pattern.match(re.sub(r'\s+', '', msg))
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
                               id=self.id_count)
        self.reply = reply.set_timed_task_success(params, res.group(7))
        return True
