#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re
import tag_controller
KEY_HELP = 'help'
KEY_SPLIT = '#'

class Help:
    """help info system"""
    help_dict = {}
    def __init__(self):
        """init"""
        # keyword-content dictionary
        self.reply = ''
    def handle_msg(self, text, to_bot):
        """handle help command"""
        if not to_bot:
            return False
        self.reply = ''
        revised_text = re.sub(r'\s+', '', text)
        if revised_text == KEY_HELP:
            self.reply = self.all()
            return True
        pattern = re.compile(r'^' + KEY_HELP + KEY_SPLIT + r'(.*?)$')
        res = pattern.match(revised_text)
        if res is not None:
            if res.group(1) in self.help_dict.keys():
                self.reply = self.help_dict[res.group(1)]
            else:
                self.reply = self.no_such_method()
            return True
        return False

    @classmethod
    def all(cls):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in cls.help_dict])
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
        return 'To tag a message, quote it and say the tag to the bot'

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
