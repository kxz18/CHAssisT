#!/usr/bin/python
# -*- coding:utf-8 -*-
"""test database class"""
import os
import sys
sys.path.append("src")
from datetime import datetime
from data.database import Database, PrimaryKey, Field

TABLE = "test_table"
PATH = "test.db"
config = 'database_config.pkl'

def test_create():
    """create table"""
    try:
        os.remove(PATH)
    except FileNotFoundError:
        pass
    database = Database(PATH)
    primary_key = PrimaryKey.id_as_primary()
    fields = [Field("msg", "TEXT"), Field("tags", "CHAR(50)"),
              Field('time', 'CHAR(30)', others=[f'DEFAULT (\'{str(datetime.now())}\')'])]
    database.create_table(TABLE, primary_key, fields)
    assert TABLE in database.tables.keys()
    database.close()

def test_insert():
    """insert data"""
    database = Database(PATH)
    database.insert(TABLE, ["msg", "tags"], ["hehe", "no use"])
    database.insert(TABLE, ["msg", "tags"], ["meeting at 9:00", "meeting time"])
    database.insert(TABLE, ["msg", "tags"], ["what?", "meeting time"])
    assert database.search(TABLE, 'id', 2) is not None
    assert len(database.search(TABLE, 'tags', 'meeting time')) == 2
    database.close()

def test_update():
    """update"""
    database = Database(PATH)
    database.update(TABLE, ["msg"], ["meeting at 8:00"], "id", 2)
    assert database.search(TABLE, 'id', 2)[0][1] == "meeting at 8:00"
    database.close()

def test_delete():
    database = Database(PATH)
    assert len(database.search(TABLE, 'id', 1)) == 1
    database.delete(TABLE, "id", 1)
    assert len(database.search(TABLE, 'id', 1)) == 0
    database.close()

def test_select():
    """test select function"""
    database = Database(PATH)
    assert len(database.select(TABLE, ['id', 'tags'])) == 2

def test_delete_by_time():
    """test delete by time range"""
    database = Database(PATH)
    data_num = len(database.select(TABLE))
    start = datetime.now()
    database.insert(TABLE, ["msg", "tags", 'time'],
                    ["delete by time", "create time", f'{str(datetime.now())}'])
    end = datetime.now()
    database.delete_by_time(TABLE, 'time', start, end)
    assert len(database.select(TABLE)) == data_num
