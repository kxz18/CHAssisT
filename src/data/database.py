#!/usr/bin/python
# -*- coding:utf-8 -*-
"""designed API for database"""
import sqlite3

class Field:
    """class of a field in database"""
    def __init__(self, name, dtype, null=True, others=None):
        """attributes:
            name: name of field
            dtype: data type
            null: can be null or not
            others: other attributes, like autoincrement"""
        self.name = name
        self.dtype = dtype
        self.null = null
        self.others = others

    def to_list(self):
        """turn attributes to list"""
        elements = [self.name, self.dtype]
        if not self.null:
            elements.append("NOT NULL")
        if isinstance(self.others, list):
            elements += self.others
        return elements

    def to_str(self):
        """turn attributes to string"""
        return " ".join(self.to_list())

class PrimaryKey(Field):
    """primary key class"""

    def to_list(self):
        """turn attributes to list"""
        elements = super(PrimaryKey, self).to_list()
        elements.insert(1, "PRIMARY KEY")
        return elements

    @classmethod
    def id(cls):
        """use auto incremental int id as primary key"""
        return PrimaryKey(name="id", dtype="INT",\
                null=False, others=["AUTOINCREMENT"])

class Database:
    """use sqlite as database"""
    def __init__(self, path):
        """params:
            path: path of data file"""
        # data path
        self.path = path
        # connect to sqlite
        self.conn = sqlite3.connect(path)

    def create_table(self, tname, primary, fields):
        """create a table
        params:
            tname: name of the table
            primary: attributes of primary key
            fields: list of fields, each is a list
        """
        cursor = self.conn.cursor()
        cursor.execute(f'''CREATE TABLE {tname}\
            ({primary.to_str()}, {','.join([field.to_str() for field in fields])});)
        ''')
        self.conn.commit()

    def insert(self, tname, keys, values):
        """insert into table
        params:
            tname: name of table
            keys: name of fields
            values: corresponding values"""
        cursor = self.conn.cursor()
        cursor.execute(f'''INSERT INTO {tname} ({','.join(keys)})\
                VALUES ({','.join(values)})''')
        self.conn.commit()
