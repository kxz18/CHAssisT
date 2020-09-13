#!/usr/bin/python
# -*- coding:utf-8 -*-
"""defination of help system"""
from tagging_modules import tag_controller
from tagging_modules import display
from timed_task_modules import task_controller


groupchat_bot_help_en = {
    'save': 'To tag a message, quote it and say the tag to the bot.'
            'If you want to add expiry date to it, append '
            f'{tag_controller.KEY_EXPIRY}{tag_controller.KEY_SPLIT}'
            f'year-month-day (hour:minute:second)',
    'delete': 'To delete a message, say to the bot like:'
              f' {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}id.'
              'Id can be obtained by displaying messages',
    'timed-delete': 'To set timed task for deleting tagged messages, say to the bot like:\n'
                    f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                    'month-day-day of week-hour-minute-x, '
                    'where messages that are x days before will be deleted and * means "every".'
                    f'e.g. {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                    '*-*-*-22-0-1 means delete messages 1 days before on 22:00 daily.\n'
                    'To stop it, say to the bot like:\n'
                    f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                    f'{tag_controller.KEY_STOP}',
    'display': 'To display all saved messages, say to the bot like:\n'
               f'{display.KEY_DISPLAY}\n'
               'To display saved messages within a time range:\n'
               f'{display.KEY_DISPLAY}{display.KEY_SPLIT}'
               'year.month.day - year.month.day\n'
               f'e.g. {display.KEY_DISPLAY}{display.KEY_SPLIT}'
               '2020.7.20 - 2020.7.22 means display all messages'
               'between 2020.7.20 and 2020.7.22',
    'question': 'To ask for saved messages, just ask the bot what you want to know',
    'timed-task': 'To set timed task for send messages, say to the bot like:\n'
                  f'{task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'
                  'month-day-day of week-hour-minute-x, '
                  'where x will be sent and * means "every".'
                  f'e.g. {task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'
                  '*-*-*-22-0-1 means sending \'1\' on 22:00 daily.\n'
                  'You can also use date format like year-month-day hour-minute-second '
                  'to set unperiodic message'
}


groupchat_bot_help_zh = {
    '存储打标消息': '如果您想存储一条消息并打标，只需要引用它，提供标注内容并@我。\n'
              '如果你想为这条消息加上有效期，只需要在标注内容后加上：\n\n'
              f'{tag_controller.KEY_EXPIRY}{tag_controller.KEY_SPLIT}'
              f'年-月-日 (小时:分钟:秒)\n\n其中括号中的内容可以不写，默认为当天0时0分0秒。'
              '有效期过后我会自动删除该条消息。',
    '删除打标消息': '如果您想删除一条已经打标的消息，只需对我说：\n\n'
              f' {tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}消息id\n\n'
              '消息id可通过浏览打标消息获得。',
    '定时删除打标消息': '如果您想定时删除一些消息，只需要对我说：\n\n'
                f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                '月-日-星期(从1到7)-小时-分钟-x\n\n'
                'x 天之前的消息会被删除，填入*表示每个时间点都会执行。'
                f'例如"{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                '*-*-*-22-0-1"表示每天22:00时删除一天前的消息。\n'
                '如果您想停止自动删除功能，只需对我说：\n\n'
                f'{tag_controller.KEY_DELETE}{tag_controller.KEY_SPLIT}'
                f'{tag_controller.KEY_STOP}',
    '浏览打标消息': '如果您想要浏览所有存储的打标消息，只需对我说：\n\n'
              f'{display.KEY_DISPLAY}\n\n'
              '如果只想显示一定时间段内的消息，可以使用如下格式：\n\n'
              f'{display.KEY_DISPLAY}{display.KEY_SPLIT}'
              f'年.月.日 - 年.月.日\n\n'
              f'例如"{display.KEY_DISPLAY}{display.KEY_SPLIT}'
              '2020.7.20 - 2020.7.22"表示展示'
              '2020.7.20和2020.7.22之间的消息',
    '提问': '如果想从历史消息中获取一些信息，只需要直接问我你的问题即可',
    '定时消息': '如果您想设定定时发送的消息，有两种可供选择的命令格式：\n\n'
            f'{task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'
            '月-日-星期-小时-分钟-消息内容。\n\n其中填入"*"表示任意时间点。\n'
            f'例如"{task_controller.KEY_TIMED_TASK}{task_controller.KEY_SPLIT}'
            '*-*-*-22-0-1"表示每天22:00发送消息"1"\n'
            f'另一种格式是：\n\n{task_controller.KEY_TIMED_TASK}'
            f'{task_controller.KEY_SPLIT}年-月-日 小时:分钟:秒-消息内容\n\n'
            '这种格式是指定时间点发送，而前一种是周期性地发送'
}
