#!/usr/bin/python
# -*- coding:utf-8 -*-
"""The data structure of messages with tags"""
from datetime import datetime
from dateutil.parser import parse
from data.database import Field


class MsgWithTag:
    """message with tag"""
    # pylint: disable=R0913
    def __init__(self, quoted, tags, talker, expiry=None, create_time=None):
        """params:
            quoted: str, quoted message
            tags: str, tags
            talker: str, name of talker
            expiry: datetime or None, expiry date, default None"""
        self.msg: str = quoted
        self.tags = tags
        self.talker = talker
        self.expiry = expiry
        self.time = datetime.now() if create_time is None else create_time

    def to_str(self):
        """transform self to string"""
        expiry_str = '' if self.expiry is None\
                     else f' expiry: {str(self.expiry)}'
        return f'{self.msg} tags: {self.tags}' + expiry_str

    @classmethod
    def from_dict(cls, data):
        """create instance from dictionary
        params:
            data: dict"""
        date_str = data['expiry']
        date = parse(date_str) if date_str != str(None) else None
        create_time = parse(data['time'])
        return MsgWithTag(data['msg'], data['tags'],
                          data['talker'], date, create_time)

    @classmethod
    def to_fields(cls):
        """turn class to list of fields"""
        return [Field('msg', 'TEXT'),
                Field('tags', 'TEXT'),
                Field('talker', 'TEXT'),
                Field('expiry', 'CHAR(30)'),
                Field('time', 'CHAR(30)')]

    @classmethod
    def get_time_key(cls):
        """return key of time stamp"""
        return 'time'

    @classmethod
    def get_msg_key(cls):
        """return key of quoted message"""
        return 'msg'
