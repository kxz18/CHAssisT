#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re
from timed_task_modules import task_controller

KEY_HELP = 'help'
KEY_SPLIT = '#'


class Help:
    """help info system"""
    def __init__(self):
        """init"""
        self.reply = ''

    def handle_msg(self, text, to_bot):
        """handle help command"""
        if not to_bot:
            return False
        self.reply = ''
        revised_text = re.sub(r'\s+', '', text)
        if revised_text == KEY_HELP:    # display navigation help info
            self.reply = self.all()
            return True
        pattern = re.compile(r'^' + KEY_HELP + KEY_SPLIT + r'(.*?)$')
        res = pattern.match(revised_text)
        if res is not None:
            if res.group(1) in self.help_dict().keys():   # found keyword
                self.reply = self.help_dict()[res.group(1)]
            else:
                self.reply = self.no_such_method()
            return True
        return False

    def get_reply(self):
        """return reply"""
        return self.reply

    @classmethod
    def help_dict(cls):
        """return dictionary of keyword of functions"""
        help_dict = {
            'timed-task': cls.timed_task(),
        }
        return help_dict

    @classmethod
    def all(cls):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in cls.help_dict()])
        return 'To get help of certain keywords, type commands like:'\
               f'{KEY_HELP}{KEY_SPLIT}function keywords\n'\
               f'all function keywords are as follows:\n{help_keywords}'

    @classmethod
    def no_such_method(cls):
        """no corresponding method doc found"""
        return 'No such function keyword found'

    @classmethod
    def timed_task(cls):
        """help doc for timed delete"""
        return 'To set timed task for send messages, say to the bot like:\n'\
               f'{task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'\
               'year-month-day-day of week-hour-minute-x, '\
               'where x will be sent and * means "every".'\
               f'e.g. {task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'\
               '*-*-*-*-22-0-1 means sending \'1\' on 22:00 daily.\n'\
               'You can also use date format like year-month-day hour-minute-second '\
               'to set unperiodic message'
