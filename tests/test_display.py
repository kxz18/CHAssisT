#!/usr/bin/python
# -*- coding:utf-8 -*-
from datetime import datetime
import os
import sys
sys.path.append("src")
from display import Display, KEY_DISPLAY, KEY_SPLIT
from data.database import Database
from data.data_transfer import DataTransfer
from data.msg_with_tag import MsgWithTag
import reply

PATH = "test.db"
CONFIG = 'database_config.pkl'

MSG_CONTENTS = [('今天19点开会', '今天开会时间'),
                ('请大家8点前完成问卷填写', '问卷截止时间'),
                ('停车场在6号楼东侧', '停车位置'),
                ('今天我爆炸了', '李总今天的活动'),
                ('微信号容易被封', '新手需要注意的地方')]

def init_data():
    """create tag_controller"""
    for path in [PATH, CONFIG]:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
    interface = DataTransfer(Database(PATH, CONFIG))
    for quoted, tag, in MSG_CONTENTS:
        msg = MsgWithTag(quoted, tag, 'me', time=datetime.now())     # talker is not important here
        interface.save_msg(msg)
    interface.save()
    return interface

def test_display_msg():
    """test display message function"""
    start = datetime.now()
    init_data()
    end = datetime.now()
    interface = DataTransfer(Database(PATH, CONFIG))
    display = Display(interface)
    assert display.handle_msg(KEY_DISPLAY, True)
    assert len(display.reply.split('\n')) == len(MSG_CONTENTS)
    assert display.handle_msg(f'{KEY_DISPLAY}{KEY_SPLIT}'
                              f'{start.year}.{start.month}.{start.day}'
                              f'-{end.year}.{end.month}.{end.day}')
    assert len(display.reply.split('\n')) == len(MSG_CONTENTS)
