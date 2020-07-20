#!/usr/bin/python
# -*- coding:utf-8 -*-
"""replies of events"""


# TaskController
def set_timed_task_success(params, message):
    """successfully set timed delete job
    params:
        params: dictionary of time parameters of the job
        message: message which is to be sent"""
    time_point = ''
    for key in params:
        if params[key] != '*':
            time_point += f'{key} {params[key]}'
    return f'message {message} will be sent on {time_point}'
