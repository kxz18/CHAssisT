#!/usr/bin/python
# -*- coding:utf-8 -*-
"""replies of events"""
from utils.date_to_str import cron_dict_to_str


# TagController
def save_msg_success():
    """successfully saved a tagged message"""
    return '收到'
    # return 'Received'


def del_msg_success(_id):
    """successfully deleted a message"""
    return f'已删除 #{_id}'
    # return f'Deleted #{_id}'


def parse_datetime_error():
    """given date with wrong format"""
    return '日期的格式好像不太对，可以参考下帮助文档'
    # return 'date-time format error, consult the help doc for format'


def set_timed_delete_success(params, delta):
    """successfully set timed delete job
    params:
        params: dictionary of time parameters of the job
        delta: messages that are 'delta' days before will be deleted"""
    # time_point = ''
    # for key in params:
    #     if params[key] != '*':
    #         if key == 'week day':
    #             time_point += f'{key} {params[key]}'
    #         else:
    #             time_point += f'{params[key]} {key}'
    # time_point = time_point.replace('year', '年')\
    #                        .replace('month', '月')\
    #                        .replace('day', '日')\
    #                        .replace('week day', '星期')\
    #                        .replace('hour', '时')\
    #                        .replace('minute', '分')\
    #                        .replace(' ', '')
    time_point = cron_dict_to_str(params, 'zh')
    return f'{delta}天前的消息将会在以下时间点被删除: {time_point}'
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
    choices = '\n'.join([f'- {tag}' for tag in tags])
    # tip = f'Maybe you can ask with following key words ?\n{choices}'
    tip = f'我有点不确定，或许你可以在这些标注中选一个进行提问?\n{choices}'
    return tip


def is_question(text):
    """judge if text is a question"""
    for key in question_signals():
        if key in text:
            return True
    return False


def question_signals():
    """return signals indicating this is a question"""
    return ['？', '?', '么', '嘛', '吗', '呢', '啊', '什么', '怎么', '如何', '哪', '为什么',
            '几', '谁', '多少', '啥', '吧']


# display
def no_msg_found():
    """when no message can be found within given span"""
    return '貌似还没有对应的信息被存储下来'
