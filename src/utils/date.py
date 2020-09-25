#!/usr/bin/python
# -*- coding:utf-8 -*-
"""parse cron type input to dictionary,
turn various type of date to readable string"""


def parse_cron_str_to_dict(cron_str, split):
    """parse cron type str to dictionary with keys:
    month, day, week day, hour, minute"""
    cron_dict = {}
    keys = ['month', 'day', 'week day', 'hour', 'minute']
    cron_list = cron_str.split(split)
    if len(cron_list) != 5:
        raise ValueError('wrong format')
    for key, content in zip(keys, cron_list):
        if content == '*':
            cron_dict[key] = content
        elif content.isdigit():
            content = int(content) - 1 if key == 'week day' else int(content)
            cron_dict[key] = content
        else:
            raise ValueError('unrecognized value')
    return cron_dict


def cron_dict_to_str(params, language):
    """turn cron type date to readable string,
    input should be preprocessed to dictionary with
    follow keys: month, day, week day, hour, minute"""
    time_point = ''
    for key in params:
        if params[key] != '*':
            if key == 'week day':
                time_point += f'{key} {params[key]}'
            else:
                time_point += f'{params[key]} {key}'
        elif key != 'week day':
            time_point += f'every {key}'
    if language == 'zh':
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        for idx, weekday in enumerate(weekdays):
            time_point = time_point.replace(f'week day {idx}',
                                            f'星期{weekday}')
        time_point = time_point\
            .replace('month', '月')\
            .replace('day', '日')\
            .replace('hour', '时')\
            .replace('minute', '分')\
            .replace('every', '每')
        time_point = time_point.replace(' ', '')
    return time_point
