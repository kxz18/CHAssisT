#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
import sys
sys.path.append("src")
from data.database import Database
from data.data_transfer import DataTransfer
from data.msg_with_tag import MsgWithTag
import reply
from question_answering import QuestionAnswering

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
        msg = MsgWithTag(quoted, tag, 'me')     # talker is not important here
        interface.save_msg(msg)
    interface.save()
    return interface

def test_confidence_high():
    """test answer with high confidence"""
    interface = init_data()
    question_answering = QuestionAnswering(interface)
    assert question_answering.handle_msg('今天几点开会？', True)
    assert question_answering.get_reply() == MSG_CONTENTS[0][0]
    assert question_answering.handle_msg('问卷几点截止？', True)
    assert question_answering.get_reply() == MSG_CONTENTS[1][0]
    assert question_answering.handle_msg('请问停车位置在哪？', True)
    assert question_answering.get_reply() == MSG_CONTENTS[2][0]

def test_confidence_median():
    """test answer with median confidence"""
    interface = init_data()
    question_answering = QuestionAnswering(interface)
    assert question_answering.handle_msg('我车停哪', True)
    assert question_answering.get_reply() == reply.similar_answer_help([MSG_CONTENTS[2][1]])

def test_confidence_no():
    """test situation in which no answer was found"""
    interface = init_data()
    question_answering = QuestionAnswering(interface)
    assert not question_answering.handle_msg('hey man', False)
    assert question_answering.handle_msg('hey man', True)
    assert question_answering.get_reply() == reply.no_answer_found()
