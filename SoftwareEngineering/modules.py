# coding=utf-8

import sqlite3

db_path = '/Users/duxinlu/Desktop/SoftwareEngineering/student_system.db'


def connect_db():
    db = sqlite3.connect(db_path)
    return db
