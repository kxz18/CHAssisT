#!/usr/bin/python
# -*- coding:utf-8 -*-
"""test data transfer"""
import os
import sys
sys.path.append('src')
from datetime import datetime, timedelta
from data.data_transfer import DataTransfer
from data.database import Database
from data.msg_with_tag import MsgWithTag

PATH = 'test.db'

def test_create():
    """create table"""
    for path in [PATH, 'database_config.pkl']:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    interface = DataTransfer(Database(PATH))
    interface.save()

def test_save_msg(msg='hahah', tag='test tag', talker='admin',
                  expiry=None, time=None, force_create=True):
    """test save a message"""
    interface = DataTransfer(Database(PATH))
    msg = MsgWithTag(msg, tag, talker, expiry, time)
    interface.save_msg(msg, force_create=force_create)
    assert interface.get_msg_by_id(1) is not None
    interface.save()

def test_del_msg_by_id():
    """test delete a message"""
    interface = DataTransfer(Database(PATH))
    interface.del_msg_by_id(1)
    assert interface.get_msg_by_id(1) is None
    interface.save()

def test_get_all_msgs():
    """test get all messages"""
    test_save_msg('second', 'test 2', 'admin2', datetime(2020, 3, 26))
    test_save_msg('third', 'test 3')
    interface = DataTransfer(Database(PATH))
    all_msg = interface.get_all_msgs()
    _, msg = all_msg[0]
    assert len(all_msg) == 2
    assert msg.expiry == datetime(2020, 3, 26)

def test_get_all_id_and_tags():
    """test get all id and tags"""
    interface = DataTransfer(Database(PATH))
    all_data = interface.get_all_id_and_tags()
    assert len(all_data) == 2
    assert all_data[0][1] == 'test 2'
    assert all_data[1][1] == 'test 3'

def test_del_by_time():
    """test delete by time stamp"""
    interface = DataTransfer(Database(PATH))
    data_num = len(interface.get_all_msgs())
    test_save_msg(time=datetime.now() - timedelta(days=3))
    interface.del_msg_by_timedelta(timedelta(days=3))
    assert len(interface.get_all_msgs()) == data_num


def test_update():
    """test insert duplicated message with different tag"""
    interface = DataTransfer(Database(PATH))
    test_save_msg(msg='update message', tag='test update')
    data_num = len(interface.get_all_msgs())
    test_save_msg(msg='update message', tag='test update 2', force_create=False)
    all_msg = interface.get_all_msgs()
    assert len(all_msg) == data_num
    assert all_msg[-1][1].msg == 'update message'
    assert all_msg[-1][1].tags == 'test update 2'
