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

# Question Answering
def no_answer_found():
    """cannot find any answer"""
    return 'Sorry, but I really don\'t know'

def similar_answer_help(tags: list):
    """provide similar answer recommend"""
    choices = '\n'.join(tags)
    tip = f'Maybe you can ask with following key words ?\n{choices}'
    return tip
