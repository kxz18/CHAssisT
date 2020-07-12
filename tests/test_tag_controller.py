#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
sys.path.append("src")
from tag_controller import TagController, KEY_DELETE, KEY_SPLIT, KEY_EXPIRY
from data.database import Database
from data.data_transfer import DataTransfer
import reply

PATH = "test.db"
CONFIG = 'database_config.pkl'

def test_create():
    """create tag_controller"""
    for path in [PATH, CONFIG]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    controller = TagController(DataTransfer(Database(PATH, CONFIG)))


def test_not_reply():
    """not saying to the bot"""
    controller = TagController(DataTransfer(Database(PATH, CONFIG)))
    reply = controller.handle_msg(quoted='null', msg='null', talker='me', to_bot=False)
    assert not reply

def test_save_msg():
    """test save messaga"""
    controller = TagController(DataTransfer(Database(PATH)))
    ifreply = controller.handle_msg(quoted='first', msg='test save msg',
                                  talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.save_msg_success()

def test_delete():
    """test delete message"""
    controller = TagController(DataTransfer(Database(PATH)))
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}1',
                                    talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.del_msg_success(1)

def test_timed_delete():
    """test timed delete"""
    controller = TagController(DataTransfer(Database(PATH)))
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}*-*-*-2-0-0-1',
                                    talker='me', to_bot=True)
    assert ifreply
