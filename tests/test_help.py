#!/usr/bin/python
# -*- coding:utf-8 -*-
"""unit test for help system"""
from tagging_modules.help import Help

HELP = Help()
KEY_HELP = HELP.get_key_help()
KEY_SPLIT = HELP.get_key_split()


def test_help_all():
    """test doc of navigation"""
    assert HELP.handle_msg(f'{KEY_HELP}', True)
    assert HELP.get_reply() == HELP.help.all()

def test_help_individual():
    """test doc of individual function"""
    for key in HELP.help.help_dict():
        assert HELP.handle_msg(f'{KEY_HELP} {KEY_SPLIT}{key}', True)
        assert HELP.get_reply() == HELP.help.help_dict()[key]

    false_keyword = 'no such key word'
    assert HELP.handle_msg(f'{KEY_HELP}{KEY_SPLIT}{false_keyword}', True)
    assert HELP.get_reply() == HELP.help.no_such_method()
