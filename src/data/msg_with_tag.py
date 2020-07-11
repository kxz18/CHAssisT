#!/usr/bin/python
# -*- coding:utf-8 -*-
"""The data structure of messages with tags"""
from dateutil.parser import parse
from data.database import Field


class MsgWithTag:
    """message with tag"""
    def __init__(self, quoted, tags, talker, expiry=None):
        """params:
            quoted: str, quoted message
            tags: str, tags
            talker: str, name of talker
            expiry: datetime or None, expiry date, default None"""
        self.msg: str = quoted
        self.tags = tags
        self.talker = talker
        self.expiry = expiry

    @classmethod
    def from_dict(cls, data):
        """create instance from dictionary
        params:
            data: dict"""
        date_str = data['expiry']
        date = parse(date_str) if date_str != str(None) else None
        return MsgWithTag(data['msg'], data['tags'],
                          data['talker'], date)

    @classmethod
    def to_fields(cls):
        """turn class to list of fields"""
        return [Field('msg', 'TEXT'),
                Field('tags', 'TEXT'),
                Field('talker', 'TEXT'),
                Field('expiry', 'CHAR(30)')]
