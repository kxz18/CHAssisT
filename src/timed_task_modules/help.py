#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re

from timed_task_modules import task_controller


class Help:
    """help info system"""

    def __init__(self, language='zh'):
        """params:
            language: zh, en"""
        if language == 'zh':
            self.help = HelpZh()
        else:
            self.help = HelpEn()

    def handle_msg(self, text, to_bot):
        """handle help command"""
        return self.help.handle_msg(text, to_bot)

    def get_reply(self):
        """return reply"""
        return self.help.get_reply()

    def get_key_help(self):
        """return KEY_HELP"""
        return self.help.KEY_HELP

    def get_key_split(self):
        """return KEY_SPLIT"""
        return self.help.KEY_SPLIT


class HelpEn:
    """help info system, en version"""

    KEY_HELP = 'help'
    KEY_SPLIT = '#'

    def __init__(self):
        """init"""
        self.reply = ''

    def handle_msg(self, text, to_bot):
        """handle help command"""
        if not to_bot:
            return False
        self.reply = ''
        revised_text = re.sub(r'\s+', '', text)
        if revised_text == self.KEY_HELP:    # display navigation help info
            self.reply = self.all()
            return True
        pattern = re.compile(r'^' + self.KEY_HELP + self.KEY_SPLIT + r'(.*?)$')
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
        return 'This is help doc for timed task\n'\
               'To get help of certain keywords, type commands like:'\
               f'{cls.KEY_HELP}{cls.KEY_SPLIT}function keywords\n'\
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


class HelpZh:
    """help info system, zh version"""

    KEY_HELP = '帮助'
    KEY_SPLIT = '#'

    def __init__(self):
        """init"""
        self.reply = ''

    def handle_msg(self, text, to_bot):
        """handle help command"""
        if not to_bot:
            return False
        self.reply = ''
        revised_text = re.sub(r'\s+', '', text)
        if revised_text == self.KEY_HELP:    # display navigation help info
            self.reply = self.all()
            return True
        pattern = re.compile(r'^' + self.KEY_HELP + self.KEY_SPLIT + r'(.*?)$')
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
            '定时消息': cls.timed_task(),
        }
        return help_dict

    @classmethod
    def all(cls):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in cls.help_dict()])
        return '这是定时消息系统的帮助文档\n'\
               f'提供的功能如下：\n{help_keywords}\n'\
               '如果想了解具体功能的使用方法，可以给我发消息：'\
               f'{cls.KEY_HELP}{cls.KEY_SPLIT}功能名\n'

    @classmethod
    def no_such_method(cls):
        """no corresponding method doc found"""
        return '我们没有提供这样的功能哦～'

    @classmethod
    def timed_task(cls):
        """help doc for timed delete"""
        return '如果您想设定定时发送的消息，有两种可供选择的命令格式：\n'\
               f'{task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'\
               '年-月-日-星期-小时-分钟-消息内容。其中填入"*"表示任意时间点。'\
               f'e.g. {task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'\
               '*-*-*-*-22-0-1 表示每天22:00发送消息"1"\n'\
               '另一种时间格式是：年-月-日 小时-分钟-秒，这种格式是指定时间点发送，'\
               '而前一种是周期性地发送'
