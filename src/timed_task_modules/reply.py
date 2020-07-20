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
            time_point += f'{key} {params[key]}'
    return f'message {message} will be sent on every {time_point}'


def set_date_timed_task_success(date, message):
    """successfully set date type timed task
    params:
        date: date to sent
        message: message to be sent"""
    return f'message {message} will be sent on {date}'
