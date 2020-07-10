#!/usr/bin/python
# -*- coding:utf-8 -*-
"""test data transfer"""
import os
import sys
sys.path.append('src')
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

def test_save_msg(msg='hahah', tag='test tag'):
    """test save a message"""
    interface = DataTransfer(Database(PATH))
    msg = MsgWithTag(msg, tag)
    interface.save_msg(msg)
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
    test_save_msg('second', 'test 2')
    test_save_msg('third', 'test 3')
    interface = DataTransfer(Database(PATH))
    assert len(interface.get_all_msgs()) == 2

def test_get_all_id_and_tags():
    """test get all id and tags"""
    interface = DataTransfer(Database(PATH))
    all_data = interface.get_all_id_and_tags()
    assert len(all_data) == 2
    assert all_data[0][1] == 'test 2'
    assert all_data[1][1] == 'test 3'
