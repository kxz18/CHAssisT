#!/usr/bin/python
# -*- coding:utf-8 -*-
"""designed API for database"""
import sqlite3
import pickle

class Field:
    """class of a field in database"""
    def __init__(self, name, dtype, null=True, others=None):
        """attributes:
            name: name of field
            dtype: data type
            null: can be null or not
            others: other attributes"""
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
        elements.insert(2, "PRIMARY KEY")
        return elements

    @classmethod
    def id_as_primary(cls):
        """use auto incremental int id as primary key"""
        return PrimaryKey(name="id", dtype="INTEGER",\
                null=False)

class Table:
    """store information of a table"""
    def __init__(self, tname, primary, fields):
        """params:
            tname: name of table
            primary: Primary, primary key
            fields: list<Field>, all fields information"""
        self.name = tname
        self.primary = primary
        self.fields = {}
        for field in [primary] + fields:
            self.fields[field.name] = field

    def get_field(self, fname):
        """return selected field info
        params:
            fname: name of field"""
        return self.fields[fname]

    def get_primary_key(self):
        """return primary key"""
        return self.primary

    def get_all_fields_name(self):
        """return all fields name"""
        return list(self.fields.keys())

    def revise_data(self, field, value):
        """to surround text and char() type data with
           a pair of ''
        params:
            field: name of field
            value: raw value"""
        dtype = self.get_field(field).dtype.lower()
        if dtype == 'text' or dtype.find('char') != -1:
            value = f'\'{value}\''
        return value

class Database:
    """use sqlite as database"""
    def __init__(self, path, config_path="database_config.pkl"):
        """params:
            path: path of data file
            cofig_path: path of database config file"""
        # data path
        self.path = path
        # connect to sqlite
        self.conn = sqlite3.connect(path)
        # store tables and their fields for type checking
        try:
            with open(config_path, 'rb') as config:
                self.tables = pickle.load(config)
        except FileNotFoundError:
            self.tables = {}
        self.config_path = config_path

    def reconnect(self):
        """reconnect to database"""
        self.close()
        self.conn = sqlite3.connect(self.path)

    def close(self):
        """close current connection to save changes to file"""
        self.conn.close()
        with open(self.config_path, 'wb') as fout:
            pickle.dump(self.tables, fout)

    def create_table(self, tname, primary, fields):
        """create a table
        params:
            tname: name of the table
            primary: attributes of primary key
            fields: list of fields, each is a list
        """
        cursor = self.conn.cursor()
        cursor.execute(f"CREATE TABLE {tname}"
                       f"({primary.to_str()}, "
                       f"{','.join([field.to_str() for field in fields])});")
        self.conn.commit()
        # store table locally
        self.tables[tname] = Table(tname, primary, fields)

    def insert(self, tname, keys, values):
        """insert into table
        params:
            tname: name of table
            keys: name of fields
            values: corresponding values"""
        # revise values, as TEXT or CHAR() must be surrounded by a pair of ''
        table = self.tables[tname]
        for idx, key in enumerate(keys):
            values[idx] = table.revise_data(key, values[idx])
        # start inserting
        cursor = self.conn.cursor()
        cursor.execute(f"INSERT INTO {tname} ({','.join(keys)}) "
                       f"VALUES ({','.join(values)})")
        self.conn.commit()

    def search(self, tname, key, value, columns=None):
        """search by id in selected table
        params:
            tname: name of table
            key: selected key
            value: value of selected key
            columns: required fields, default all
        return:
            tuple of values of selected columns"""
        # initialize columns
        if columns is None:
            columns = ['*']

        table = self.tables[tname]
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT {','.join(columns)} from {tname} "
                       f"where {key}={table.revise_data(key, value)}")
        return cursor.fetchall() if cursor.rowcount != 0 else None

    def update(self, tname, keys, values, key=None, value=None):
        """update values of selected rows
        params:
            tname: name of table
            keys: list<str>, fields needed updating
            values: list, updating values
            key: str, search key
            value: search value
        return:
            True or False"""
        table = self.tables[tname]
        # form update sequence
        update_seq = ','.join([field+'='+str(table.revise_data(field, values[idx]))\
                for idx, field in enumerate(keys)])
        # form where subcmd
        where = ''
        if key is not None:
            where = f"where {key}={table.revise_data(key, value)}"
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE {tname} set "
                       f"{update_seq} {where};")
        self.conn.commit()
        return True

if __name__ == "__main__":
    TABLE = "test_table"
    PATH = "test.db"
    import os
    try:
        os.remove(PATH)
    except FileNotFoundError:
        pass
    # create database
    database = Database(PATH)
    primary_key = PrimaryKey.id_as_primary()
    fields = [Field("msg", "TEXT"), Field("tags", "CHAR(50)")]
    database.create_table(TABLE, primary_key, fields)
    database.insert(TABLE, ["msg", "tags"], ["hehe", "no use"])
    database.insert(TABLE, ["msg", "tags"], ["meeting at 9:00", "meeting time"])
    database.insert(TABLE, ["msg", "tags"], ["what?", "meeting time"])
    print(database.search(TABLE, 'id', 2))
    print(database.search(TABLE, 'tags', 'meeting time'))
    database.update(TABLE, ["msg"], ["meeting at 8:00"], "id", 2)
    print(database.search(TABLE, 'id', 2))
    database2 = Database(PATH)
    print(database2.search(TABLE, 'id', 2))
    
