#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from wechaty import Contact
from timed_task_modules.task_controller import TaskController, KEY_TIMED_TASK, KEY_SPLIT

def test_date_pattern():
    """test date pattern timed task"""
    controller = TaskController()
    date = datetime.now() + timedelta(hours=1)
    command = KEY_TIMED_TASK + KEY_SPLIT + f'{str(date)}-test message'
    contact = Contact(1)
    assert controller.handle_msg(command, contact, True)

def test_cron_pattern():
    """test cron pattern timed task"""
    controller = TaskController()
    command = KEY_TIMED_TASK + KEY_SPLIT\
              + '2019-7-3-*-22-13-test message'
    contact = Contact(1)
    assert controller.handle_msg(command, contact, True)
