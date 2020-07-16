#!/usr/bin/python
# -*- coding:utf-8 -*-
"""replies of events"""
# TagController
def save_msg_success():
    """successfully saved a tagged message"""
    return 'Received'

def del_msg_success(_id):
    """successfully deleted a message"""
    return f'Deleted #{_id}'

def parse_expiry_error():
    """given expiry date with wrong format"""
    return 'Expiry format error, consult the help doc for format'

def set_timed_delete_success(params, delta):
    """successfully set timed delete job
    params:
        params: dictionary of time parameters of the job
        delta: messages that are 'delta' days before will be deleted"""
    time_point = ''
    for key in params:
        if params[key] != '*':
            time_point += f'{key} {params[key]}'
    return f'messages that are {delta} days before will be deleted on every {time_point}'

def stop_timed_delete(success):
    """return reply of stopping timed delete according to success status"""
    if success:
        return 'Successfully stoped timed delete'
    else:
        return 'No timed delete task running'

# Question Answering
def no_answer_found():
    """cannot find any answer"""
    return 'Sorry, but I really don\'t know'

def similar_answer_help(tags: list):
    """provide similar answer recommend"""
    choices = '\n'.join(tags)
    tip = f'Maybe you can ask with following key words ?\n{choices}'
    return tip
