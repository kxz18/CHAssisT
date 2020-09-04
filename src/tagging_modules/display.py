#!/usr/bin/python
# -*- coding:utf-8 -*-
"""ddfination of class display"""
from typing import Optional
from datetime import datetime, timedelta
import re
from dateutil.parser import parse
from dateutil.parser._parser import ParserError

from data.data_transfer import DataTransfer
from tagging_modules import reply

KEY_DISPLAY = '浏览'
# KEY_DISPLAY = 'display'
KEY_SPLIT = r'#'


class Display:
    """handle display command"""
    def __init__(self, interface: DataTransfer):
        """params:
            interface: interface of database"""
        self.interface = interface
        self.reply = ''

    def get_reply(self):
        """return reply message"""
        return self.reply

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
        if len(msgs_in_time_range) == 0:
            return reply.no_msg_found()
        return '\n'.join([f'#{_id} ' + msg.to_str() for _id, msg in msgs_in_time_range])

    def handle_display_msgs(self, text):
        """display msgs, pattern is like:
        display(key):(split) year.month.day - year.month.day"""
        revised_text = re.sub(r'\s+', '', text)
        no_time_pattern = re.compile(r'^' + KEY_DISPLAY + r'$')
        res = no_time_pattern.match(revised_text)
        if res is not None:     # matched
            self.reply = self.display_msgs_by_time_range(None, None)
            return True
        with_time_pattern = re.compile(r'^' + KEY_DISPLAY + KEY_SPLIT
                                       + r'(.*?)-(.*?)$')
        res = with_time_pattern.match(revised_text)
        if res is not None:
            try:
                start = parse(res.group(1))
                # as 2020.7.20 includes messages from 2020.7.20 0:0 to 23:59
                end = parse(res.group(2)) + timedelta(days=1) - timedelta(seconds=1)
                self.reply = self.display_msgs_by_time_range(start, end)
            except ParserError:     # wrong datetime format
                self.reply = reply.parse_datetime_error()
            return True
        return False
