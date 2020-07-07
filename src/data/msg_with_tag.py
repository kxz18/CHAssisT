#!/usr/bin/python
# -*- coding:utf-8 -*-
"""The data structure of messages with tags"""

class MsgWithTags:
    """message with tag"""
    def __init__(self, quoted, reply):
        self.quoted: str = quoted
        self.tags = MsgWithTags.getTagsFromMsg(reply)

