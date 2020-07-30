#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
import re
from langdetect import detect


class Help:
    """help info system, en version"""

    def __init__(self, key_help, key_split, help_dict):
        """init"""
        self.reply = ''
        self.key_help = key_help
        self.key_split = key_split
        self.help_dict = help_dict
        self.lang = detect(list(help_dict.values())[0])

    def handle_msg(self, text, to_bot):
        """handle help command"""
        if not to_bot:
            return False
        self.reply = ''
        revised_text = re.sub(r'\s+', '', text)
        if revised_text == self.key_help:    # display navigation help info
            self.reply = self.all()
            return True
        pattern = re.compile(r'^' + self.key_help + self.key_split + r'(.*?)$')
        res = pattern.match(revised_text)
        if res is not None:
            if res.group(1) in self.help_dict.keys():   # found keyword
                self.reply = self.help_dict[res.group(1)]
            else:
                self.reply = self.no_such_method()
            return True
        return False

    def get_reply(self):
        """return reply"""
        return self.reply

    def all(self):
        """all help information"""
        help_keywords = '\n'.join([f'- {key}' for key in self.help_dict])
        first_key = list(self.help_dict.keys())[0]
        if self.lang == 'zh-cn':
            return '这是各种功能的帮助文档\n'\
                   f'提供的功能如下：\n{help_keywords}\n'\
                   '如果想了解具体功能的使用方法，可以用这样的格式给我发消息：\n\n'\
                   f'{self.key_help}{self.key_split}功能名\n\n'\
                   f'例如想了解功能"{first_key}"的详细信息，可以发送'\
                   f'"{self.key_help}{self.key_split}{first_key}"向我发问'

        return 'This is help doc for all functions\n'\
               'To get help of certain keywords, type commands like:'\
               f'{self.key_help}{self.key_split}function keywords\n'\
               f'all function keywords are as follows:\n{help_keywords}'

    def no_such_method(self):
        """no corresponding method doc found"""
        if self.lang == 'zh-cn':
            return '我们没有提供这样的功能哦～'
        return 'No such function keyword found'
