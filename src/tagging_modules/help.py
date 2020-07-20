#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re


from tagging_modules import tag_controller
from tagging_modules import display
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
        return 'To get help of certain keywords, type commands like:'\
               f'{KEY_HELP}{KEY_SPLIT}function keywords\n'\
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
