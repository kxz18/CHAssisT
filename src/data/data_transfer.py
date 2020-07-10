#!/usr/bin/python
# -*- coding:utf-8 -*-
"""interface between msg with tags and database"""
from data.database import Database, PrimaryKey
from data.msg_with_tag import MsgWithTag

class DataTransfer:
    """Transfer msg with tags class to database"""
    def __init__(self, database: Database, tname="Messages"):
        """params:
            database: Database instance
            tname: name of table to store information"""
        self.database = database
        self.tname = tname
        self.primary_key = PrimaryKey.id_as_primary().name
        self.fields = MsgWithTag.to_fields() # no auto-increment id
        # create table
        if tname not in database.get_all_tables_name():
            database.create_table(tname, PrimaryKey.id_as_primary(), self.fields)

    def data_to_msg(self, data):
        """turn data fetched from database to MsgWithTag instance
        params:
            data: data fetched from database(tuple)"""
        fields_names = [self.primary_key] + [field.name for field in self.fields]
        data_dict = {}
        for idx, field in fields_names:
            data_dict[field] = data[idx]
        return MsgWithTag.from_dict(data_dict)

    def save_msg(self, msg: MsgWithTag):
        """save tagged message
        params:
            msg: tagged message"""
        data_dict = msg.__dict__
        self.database.insert(self.tname, list(data_dict.keys()),\
                list(data_dict.values()))

    def del_msg_by_id(self, value):
        """delete stored message by id number
        params:
            value: id number"""
        self.database.delete(self.tname, self.primary_key, value)

    def get_msg_by_id(self, value):
        """return MsgWithTag instance of selected message
        params:
            value: id number"""
        msg_data = self.database.search(self.tname,\
                self.primary_key, value)
        if len(msg_data) != 0:
            return self.data_to_msg(msg_data[0]) # id is unique
        return None

    def get_all_msgs(self):
        """return all stored tagged messages
        return:
            list of tuple(id, MsgWithTag instance)"""
        data = self.database.select(self.tname)
        msgs = []
        for item in data:
            msgs.append((item[0], self.data_to_msg(item)))
        return msgs

    def get_all_id_and_tags(self):
        """return list of tuples(id, tags)"""
        return self.database.select(self.tname,\
                [self.primary_key, 'tags'])
