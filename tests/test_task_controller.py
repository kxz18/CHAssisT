#!/usr/bin/python
# -*- coding:utf-8 -*-
from time import sleep
import asyncio
from datetime import datetime, timedelta
from wechaty import Contact
from timed_task_modules.task_controller import TaskController, KEY_TIMED_TASK, KEY_SPLIT

class FakeContact:
    """with only said content and say function"""

    def __init__(self):
        """last said sentences are stored in said"""
        self.said = ''

    async def say(self, content):
        """store content in said"""
        self.said = content


def test_date_pattern():
    """test date pattern timed task"""

    contact = FakeContact()
    test_msg = 'this is a test message'
    date = datetime.now() + timedelta(seconds=1)
    async def task():
        controller = TaskController()
        command = KEY_TIMED_TASK + KEY_SPLIT + f'{str(date)}-{test_msg}'
        assert controller.handle_msg(command, contact, True)

    asyncio.run(task())


def test_cron_pattern():
    """test cron pattern timed task"""
    
    async def task():
        controller = TaskController()
        command = KEY_TIMED_TASK + KEY_SPLIT\
                  + '7-3-*-22-13-test message'
        contact = FakeContact()
        assert controller.handle_msg(command, contact, True)

    asyncio.run(task())
