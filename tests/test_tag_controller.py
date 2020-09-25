#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from time import sleep
from datetime import datetime, timedelta
from tagging_modules.tag_controller import TagController, KEY_DELETE, KEY_SPLIT, KEY_EXPIRY, KEY_STOP
from data.database import Database
from data.data_transfer import DataTransfer
from tagging_modules import reply

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
    interface = DataTransfer(Database(PATH))
    controller = TagController(interface)
    ifreply = controller.handle_msg(quoted='first', msg='test save msg',
                                  talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.save_msg_success()
    assert len(interface.get_all_msgs()) == 1

def test_expiry():
    """test expiry of messages"""
    interface = DataTransfer(Database(PATH))
    controller = TagController(interface)
    data_num = len(interface.get_all_msgs())
    expiry = datetime.now() + timedelta(seconds=1)
    msg = f'test expiry, {KEY_EXPIRY}{KEY_SPLIT}{str(expiry)}'
    controller.handle_msg(quoted='second', msg=msg,
                          talker='me', to_bot=True)
    sleep(1)
    assert data_num == len(interface.get_all_msgs())

def test_delete():
    """test delete message"""
    interface = DataTransfer(Database(PATH))
    controller = TagController(interface)
    data_num = len(interface.get_all_msgs())
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}1',
                                    talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.del_msg_success(1)
    assert len(interface.get_all_msgs()) == data_num - 1

def test_timed_delete():
    """test timed delete"""
    controller = TagController(DataTransfer(Database(PATH)))
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}*-*-2-0-0-1',
                                    talker='me', to_bot=True)
    assert ifreply
    # substitute former plan
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}*-*-*-*-*-1',
                                    talker='me', to_bot=True)
    assert ifreply

def test_wrong_cron_format():
    """test timed delete with wrong format"""
    controller = TagController(DataTransfer(Database(PATH)))
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}*-*-0-0-0-1',
                                    talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.parse_datetime_error()

def test_stop_timed_delete():
    """test stop timed delete task"""
    controller = TagController(DataTransfer(Database(PATH)))
    controller.handle_msg(quoted=None, msg=f'{KEY_DELETE} {KEY_SPLIT}*-*-2-0-0-1',
                          talker='me', to_bot=True)
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE}{KEY_SPLIT}{KEY_STOP}',
                                    talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.stop_timed_delete(True)
    ifreply = controller.handle_msg(quoted=None, msg=f'{KEY_DELETE}{KEY_SPLIT}{KEY_STOP}',
                                    talker='me', to_bot=True)
    assert ifreply
    assert controller.reply == reply.stop_timed_delete(False)
