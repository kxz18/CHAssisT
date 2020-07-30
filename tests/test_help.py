#!/usr/bin/python
# -*- coding:utf-8 -*-
"""unit test for help system"""
from help_modules.help import Help
from help_modules.example_dict import groupchat_bot_help_zh

KEY_HELP = '帮助'
KEY_SPLIT = '#'
HELP = Help(KEY_HELP, KEY_SPLIT, groupchat_bot_help_zh)


def test_help_all():
    """test doc of navigation"""
    assert HELP.handle_msg(f'{KEY_HELP}', True)
    assert HELP.get_reply() == HELP.all()

def test_help_individual():
    """test doc of individual function"""
    for key in HELP.help_dict:
        assert HELP.handle_msg(f'{KEY_HELP} {KEY_SPLIT}{key}', True)
        assert HELP.get_reply() == HELP.help_dict[key]

    false_keyword = 'no such key word'
    assert HELP.handle_msg(f'{KEY_HELP}{KEY_SPLIT}{false_keyword}', True)
    assert HELP.get_reply() == HELP.no_such_method()
