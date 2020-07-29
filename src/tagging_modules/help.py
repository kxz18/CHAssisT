#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re

from tagging_modules import tag_controller
from tagging_modules import display


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
            'save': cls.save_msg(),
            'delete': cls.delete_msg(),
            'timed-delete': cls.timed_delete(),
            'display': cls.display_msg(),
            'question': cls.question_answering()
        }
        return help_dict

    @classmethod
    def all(cls):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in cls.help_dict()])
        return 'This is help doc for tagging system\n'\
               'To get help of certain keywords, type commands like:'\
               f'{cls.KEY_HELP}{cls.KEY_SPLIT}function keywords\n'\
               f'all function keywords are as follows:\n{help_keywords}'

    @classmethod
    def no_such_method(cls):
        """no corresponding method doc found"""
        return 'No such function keyword found'

    @classmethod
    def save_msg(cls):
        """help doc for save tagged message"""
        return 'To tag a message, quote it and say the tag to the bot.'\
               'If you want to add expiry date to it, append '\
               f'{tag_controller.KEY_EXPIRY}{tag_controller.KEY_SPLIT}'\
               f'year-month-day (hour:minute:second)'

    @classmethod
    def delete_msg(cls):
        """help doc for delete certain message"""
        return 'To delete a message, say to the bot like:'\
               f' {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}id.'\
               'Id can be obtained by displaying messages'

    @classmethod
    def timed_delete(cls):
        """help doc for timed delete"""
        return 'To set timed task for deleting tagged messages, say to the bot like:\n'\
               f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'\
               'year-month-day-day of week-hour-minute-x, '\
               'where messages that are x days before will be deleted and * means "every".'\
               f'e.g. {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'\
               '*-*-*-*-22-0-1 means delete messages 1 days before on 22:00 daily.\n'\
               'To stop it, say to the bot like:\n'\
               f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}{tag_controller.KEY_STOP}'

    @classmethod
    def display_msg(cls):
        """return help for displaying"""
        return 'To display all saved messages, say to the bot like:\n'\
               f'{display.KEY_DISPLAY}\n'\
               'To display saved messages within a time range:\n'\
               f'{display.KEY_DISPLAY}{display.KEY_SPLIT}'\
               'year.month.day - year.month.day\n'\
               f'e.g. {display.KEY_DISPLAY}{display.KEY_SPLIT}'\
               '2020.7.20 - 2020.7.22 means display all messages'\
               'between 2020.7.20 and 2020.7.22'

    @classmethod
    def question_answering(cls):
        """return help for question answering"""
        return 'To ask for saved messages, just ask the bot what you want to know'


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
            '存储打标消息': cls.save_msg(),
            '删除打标消息': cls.delete_msg(),
            '定时删除打标消息': cls.timed_delete(),
            '浏览打标消息': cls.display_msg(),
            '提问': cls.question_answering()
        }
        return help_dict

    @classmethod
    def all(cls):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in cls.help_dict()])
        return '这是消息打标系统的帮助文档\n'\
               f'提供的功能如下：\n{help_keywords}\n'\
               '如果想了解具体功能的使用方法，可以给我发消息：'\
               f'{cls.KEY_HELP}{cls.KEY_SPLIT}功能名\n'

    @classmethod
    def no_such_method(cls):
        """no corresponding method doc found"""
        return '我们没有提供这样的功能哦～'

    @classmethod
    def save_msg(cls):
        """help doc for save tagged message"""
        return '如果您想存储一条消息并打标，只需要引用它，提供标注内容并@我。'\
               '如果你想为这条消息加上有效期，只需要在标注内容后加上：'\
               f'{tag_controller.KEY_EXPIRY}{tag_controller.KEY_SPLIT}'\
               f'年-月-日 (小时:分钟:秒)。其中括号中的内容可以不写，默认为当天0时0分0秒。'\
               '有效期过后我会自动删除该条消息。'

    @classmethod
    def delete_msg(cls):
        """help doc for delete certain message"""
        return '如果您想删除一条已经打标的消息，只需对我说：'\
               f' {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}消息id。'\
               '消息id可通过浏览打标消息获得。'

    @classmethod
    def timed_delete(cls):
        """help doc for timed delete"""
        return '如果您想定时删除一些消息，只需要对我说：'\
               f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'\
               '年-月-日-星期(从1到7)-小时-分钟-x。'\
               'x 天之前的消息会被删除，填入*表示每个时间点都会执行。'\
               f'e.g. {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'\
               '*-*-*-*-22-0-1 表示每天22:00时删除一天前的消息。\n'\
               '如果您想停止自动删除功能，只需对我说：\n'\
               f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}{tag_controller.KEY_STOP}'

    @classmethod
    def display_msg(cls):
        """return help for displaying"""
        return '如果您想要浏览所有存储的打标消息，只需对我说：\n'\
               f'{display.KEY_DISPLAY}\n'\
               '如果只想显示一定时间段内的消息，可以使用如下格式：\n'\
               f'{display.KEY_DISPLAY}{display.KEY_SPLIT}'\
               f'年.月.日 - 年.月.日\n'\
               f'e.g. {display.KEY_DISPLAY}{display.KEY_SPLIT}'\
               '2020.7.20 - 2020.7.22 表示展示'\
               '2020.7.20和2020.7.22之间的消息'

    @classmethod
    def question_answering(cls):
        """return help for question answering"""
        return '如果想从历史消息中获取一些信息，只需要直接问我你的问题即可'
