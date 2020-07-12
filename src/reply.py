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
