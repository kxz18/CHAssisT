#!/usr/bin/python
# -*- coding:utf-8 -*-
"""replies of events"""


# TagController
def save_msg_success():
    """successfully saved a tagged message"""
    return '收到'
    # return 'Received'


def del_msg_success(_id):
    """successfully deleted a message"""
    return f'已删除 #{_id}'
    # return f'Deleted #{_id}'


def parse_expiry_error():
    """given expiry date with wrong format"""
    return '有效期的格式好像不太对，可以参考下帮助文档'
    # return 'Expiry format error, consult the help doc for format'


def set_timed_delete_success(params, delta):
    """successfully set timed delete job
    params:
        params: dictionary of time parameters of the job
        delta: messages that are 'delta' days before will be deleted"""
    time_point = ''
    for key in params:
        if params[key] != '*':
            time_point += f'{key} {params[key]}'
    return f'{delta}天前的消息将会在每个{time_point}被删除'
    # return f'messages that are {delta} days before will be deleted on every {time_point}'


def stop_timed_delete(success):
    """return reply of stopping timed delete according to success status"""
    if success:
        return '成功停止定时删除'
        # return 'Successfully stoped timed delete'
    return '目前没有定时删除的任务正在进行'
    # return 'No timed delete task running'


# Question Answering
def no_answer_found():
    """cannot find any answer"""
    return '不好意思，这个问题我似乎不知道答案'
    # return 'Sorry, but I really don\'t know'


def similar_answer_help(tags: list):
    """provide similar answer recommend"""
    choices = '\n'.join(tags)
    # tip = f'Maybe you can ask with following key words ?\n{choices}'
    tip = f'我有点不确定，或许你可以在这些标注中选一个进行提问?\n{choices}'
    return tip
