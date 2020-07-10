#!/usr/bin/python
# -*- coding:utf-8 -*-
"""test database class"""
import os
import sys
sys.path.append("src")
from data.database import Database, PrimaryKey, Field

TABLE = "test_table"
PATH = "test.db"

def test_create():
    """create table"""
    try:
        os.remove(PATH)
    except FileNotFoundError:
        pass
    database = Database(PATH)
    primary_key = PrimaryKey.id_as_primary()
    fields = [Field("msg", "TEXT"), Field("tags", "CHAR(50)")]
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
