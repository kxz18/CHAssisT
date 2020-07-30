#!/usr/bin/python
# -*- coding:utf-8 -*-
"""functions for extracting quoted text, text and mentioned contact
from message obtained from wechat"""
import re


def split_quote_and_mention(text):
    """split quoted text, reply text and mention"""
    quoted, text_and_mention = split_quote(text)
    reply, mention = split_mention(text_and_mention)
    return (quoted, reply, mention)


def split_quote(text):
    """split quoted text and reply from given text,
    the pattern is like "talker: quoted"\n(several -)\nreply
    return: (quoted, text and mentions)"""
    pattern = re.compile(r'(.*?)\n' + r'[-| ]*' + r'\n(.*?)$')
    res = pattern.match(text)
    if res is None:
        return (None, text)
    return (res.group(1), res.group(2))


def split_mention(text):
    """split @sb from given text,
    pattern is like: text @alias"""
    pattern = re.compile(r'(.*?)\s*@(.*?)(?:\u2005)?$')
    res = pattern.match(text)
    if res is None:
        return (text, None)
    return (res.group(1), res.group(2))
