#!/usr/bin/python
# -*- coding:utf-8 -*-
"""handle commands of saving and deleting stored messages"""
import re
from datetime import timedelta
from dateutil.parser import parse
from apscheduler.schedulers.blocking import BlockingScheduler
from data.data_transfer import DataTransfer
from data.msg_with_tag import MsgWithTag
from question_answering import QuestionAnswering

KEY_EXPIRY = '#expiry'
KEY_DELETE = 'delete'
KEY_SPLIT = r'#'

class TagController:
    """handle commands of saving and deleting stored messages"""
    def __init__(self, interface: DataTransfer):
        """params:
            interface: interface of database"""
        self.interface = interface
        self.reply = ''  # during handling, help or reply messages may be needed
        self.scheduler = BlockingScheduler()

    def handle_msg(self, quoted, msg, talker, to_bot):
        """handle commands
        params:
            quoted: str, message which is quoted
            msg: str, messages from talker
            talker: str, name of talker
            to_bot: bool, whether talking to the bot
        save, delete, timed delete, stop timed delete functions are handled here
            """
        # clear reply
        self.reply = ''
        # check if saying to the bot
        if not to_bot:
            return False
        # save message
        if self.handle_save(quoted, msg, talker):
            return True
        # delete message
        if self.handle_delete(msg):
            return True
        # timed delete
        if self.handle_timed_delete(msg):
            return True
        return False

    def get_reply(self):
        """return reply"""
        return self.reply

    def handle_save(self, quoted, msg, talker):
        """handle save function"""
        if quoted is None:
            return False
        # check if it has an expiry date
        if KEY_EXPIRY in msg:
            splited = re.split(KEY_EXPIRY + KEY_SPLIT, msg)
            content = KEY_EXPIRY.join(splited[:-1])
            date_str = splited[-1].strip()  # clear spaces at head and tail
            try:
                expiry = parse(date_str)
            except Exception:   # here help doc may be needed
                expiry = None
        else: # no expiry
            content = msg
            expiry = None
        tags = QuestionAnswering.get_tags_from_msg(content)
        self.interface.save_msg(MsgWithTag(quoted, tags, talker, expiry))
        if expiry is not None:
            # create after-expiry delete
            _id = self.interface.get_msg_by_content(quoted)[0]
            self.scheduler.add_job(self.interface.del_msg_by_id, 'date',
                                   run_date=expiry, args=[_id])
        return True

    def handle_delete(self, msg):
        """handle delete command"""
        # pattern is like 'delete#123'
        pattern = re.compile(f'{KEY_EXPIRY}' + KEY_SPLIT + r'(\d+)$')
        res = pattern.match(re.sub(r'\s+', '', msg))    # get rid of spaces
        if res is None:
            return False
        self.interface.del_msg_by_id(int(res.group(1)))
        return True

    def handle_timed_delete(self, msg: str):
        """generate timed deleting task"""
        # pattern is like 'timed delete#y-m-d-dof-h-min-x'
        # data which are x days before will be deleted
        pattern = re.compile(KEY_DELETE + KEY_SPLIT +
                             '-'.join([r'(\d+|*)' for _ in range(7)]))
        res = pattern.match(re.sub(r'\s+', '', msg))
        if res is None:
            return False
        self.scheduler.add_job(self.interface.del_msg_by_timedelta, 'cron',
                               years=res.group(1), month=res.group(2),
                               day=res.group(3), day_of_week=res.group(4),
                               hour=res.group(5), minute=res.group(6),
                               args=[timedelta(days=int(res.group(7)))])
        return True

    def handle_stop_timed_delete(self, msg: str):
        """stop timed delete task"""
