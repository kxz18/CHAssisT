#!/usr/bin/python
# -*- coding:utf-8 -*-
"""ddfination of class display"""
from typing import Optional
from datetime import datetime
import re
from dateutil.parser import parse

from data.data_transfer import DataTransfer

KEY_DISPLAY = 'display'
KEY_SPLIT = r'#'

class Display:
    """handle display command"""
    def __init__(self, interface: DataTransfer):
        """params:
            interface: interface of database"""
        self.interface = interface
        self.reply = ''

    def handle_msg(self, text, to_bot):
        """deal with display command
        params:
            text: raw message
            to_bot: if saying to the bot"""
        if not to_bot:
            return False
        self.reply = ''
        if self.handle_display_msgs(text):
            return True
        return False

    def display_msgs_by_time_range(self, start: Optional[datetime] = None,
                                   end: Optional[datetime] = None):
        """return string of messages within given time range
        params:
            start: start of time span, can be None, which means no restrict
            end: end of time span, can be None"""
        msgs_in_time_range = self.interface.get_msgs_by_time_range(start, end)
        return '\n'.join([msg.to_str() for msg in msgs_in_time_range])

    def handle_display_msgs(self, text):
        """display msgs, pattern is like:
        display(key):(split) year.month.day - year.month.day"""
        revised_text = re.sub(r'\s+', '', text)
        no_time_pattern = re.compile(r'^' + KEY_SPLIT + r'$')
        res = no_time_pattern.match(revised_text)
        if res is not None:     # matched
            self.reply = self.display_msgs_by_time_range(None, None)
            return True
        with_time_pattern = re.compile(r'^' + KEY_DISPLAY + KEY_SPLIT +
                                       r'(\d+\.\d+\.\d+)-(\d+\.\d+\.\d+)$')
        res = with_time_pattern.match(revised_text)
        if res is not None:
            self.reply = self.display_msgs_by_time_range(parse(res.group(1)),
                                                         parse(res.group(2)))
            return True
        return False
