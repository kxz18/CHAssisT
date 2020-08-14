#!/usr/bin/python
# -*- coding:utf-8 -*-
"""handle commands of saving and deleting stored messages"""
import re
from datetime import timedelta
from dateutil.parser import parse
from dateutil.parser._parser import ParserError
from apscheduler.schedulers.background import BackgroundScheduler
from data.data_transfer import DataTransfer
from data.msg_with_tag import MsgWithTag
from tagging_modules.question_answering import QuestionAnswering
from tagging_modules import reply

KEY_EXPIRY = '有效期'
KEY_DELETE = '删除'
KEY_STOP = '停止'
# KEY_EXPIRY = 'expiry'
# KEY_DELETE = 'delete'
# KEY_STOP = 'stop'
KEY_SPLIT = r'#'


class TagController:
    """handle commands of saving and deleting stored messages"""
    def __init__(self, interface: DataTransfer):
        """params:
            interface: interface of database"""
        self.interface = interface
        self.reply = ''  # during handling, help or reply messages may be needed
        self.scheduler = BackgroundScheduler()
        self.job_id = 'timed delete'
        self.scheduler.start()

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
        # stop timed delete
        if self.handle_stop_timed_delete(msg):
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
            except ParserError:   # here help doc may be needed
                self.reply = reply.parse_datetime_error()
                return True
        else:    # no expiry
            content = msg
            expiry = None
        tags = QuestionAnswering.get_tags_from_msg(content)
        self.interface.save_msg(MsgWithTag(quoted, tags, talker, expiry))
        if expiry is not None:
            # create after-expiry delete
            _id = self.interface.get_msg_by_content(quoted)[0]
            self.scheduler.add_job(self.interface.del_msg_by_id, 'date',
                                   run_date=expiry, args=[_id])
        self.reply = reply.save_msg_success()
        return True

    def handle_delete(self, msg):
        """handle delete command"""
        # pattern is like 'delete#123'
        pattern = re.compile(r'^' + KEY_DELETE + KEY_SPLIT + r'(\d+)$')
        res = pattern.match(re.sub(r'\s+', '', msg))    # get rid of spaces
        if res is None:
            return False
        _id = int(res.group(1))
        self.interface.del_msg_by_id(_id)
        self.reply = reply.del_msg_success(_id)
        return True

    def handle_timed_delete(self, msg: str):
        """generate timed deleting task"""
        # pattern is like 'delete#y-m-d-dof-h-min-x'
        # data which are x days before will be deleted
        pattern = re.compile(r'^' + KEY_DELETE + KEY_SPLIT
                             + '-'.join([r'(\d+|\*)' for _ in range(7)]))
        res = pattern.match(re.sub(r'\s+', '', msg))
        if res is None:
            return False
        ids = [job.id for job in self.scheduler.get_jobs()]
        if self.job_id in ids:   # remove former job
            self.scheduler.remove_job(self.job_id)
        params = {}
        for idx, key in enumerate(['year', 'month', 'day', 'week day', 'hour', 'minute']):
            params[key] = res.group(idx + 1)
        self.scheduler.add_job(self.interface.del_msg_by_timedelta, 'cron',
                               year=params['year'], month=params['month'],
                               day=params['day'], day_of_week=params['week day'],
                               hour=params['hour'], minute=params['minute'],
                               args=[timedelta(days=int(res.group(7)))],
                               id=self.job_id)
        self.reply = reply.set_timed_delete_success(params, int(res.group(7)))
        return True

    def handle_stop_timed_delete(self, msg: str):
        """stop timed delete task"""
        # pattern is like 'delete#stop'
        if re.sub(r'\s+', '', msg) == f'{KEY_DELETE}{KEY_SPLIT}{KEY_STOP}':
            ids = [job.id for job in self.scheduler.get_jobs()]
            if self.job_id in ids:   # remove
                self.scheduler.remove_job(self.job_id)
                self.reply = reply.stop_timed_delete(True)
            else:
                self.reply = reply.stop_timed_delete(False)
            return True
        return False
