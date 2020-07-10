#!/usr/bin/python
# -*- coding:utf-8 -*-
"""The data structure of messages with tags"""
from data.database import Field


class MsgWithTag:
    """message with tag"""
    def __init__(self, quoted, tags):
        """params:
            quoted: str, quoted message
            tags: str, tags"""
        self.msg: str = quoted
        self.tags = tags

    @classmethod
    def from_dict(cls, data):
        """create instance from dictionary
        params:
            data: dict"""
        return MsgWithTag(data['msg'], data['tags'])

    @classmethod
    def to_fields(cls):
        """turn class to list of fields"""
        return [Field('msg', 'TEXT'),
                Field('tags', 'TEXT')]
