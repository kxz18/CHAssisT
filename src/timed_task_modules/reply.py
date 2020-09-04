#!/usr/bin/python
# -*- coding:utf-8 -*-
"""replies of events"""


# TaskController
def set_cron_timed_task_success(params, message):
    """successfully set cron type timed task
    params:
        params: dictionary of time parameters of the job
        message: message which is to be sent"""
    time_point = ''
    for key in params:
        if params[key] != '*':
            if key == 'week day':
                time_point += f'{key} {params[key]}'
            else:
                time_point += f'{params[key]} {key}'
    return f'"{message}"将在每个以下时间点被发送：{time_point}'\
           .replace('year', '年')\
           .replace('month', '月')\
           .replace('day', '日')\
           .replace('week day', '星期')\
           .replace('hour', '时')\
           .replace('minute', '分')\
           .replace(' ', '')
    # return f'message {message} will be sent on every {time_point}'


def set_date_timed_task_success(date, message):
    """successfully set date type timed task
    params:
        date: date to sent
        message: message to be sent"""
    return f'"{message}"将在{date}被发出'
    # return f'message {message} will be sent on {date}'