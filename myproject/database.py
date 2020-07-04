"""
SQLite database interface.
"""
import sqlite3
import time

import settings

sql_schema = """
create table tasks (
  id        integer  primary key autoincrement,
  created   real     not null,
  finished  real,
  result    text
);
"""

def connect_db():
    return sqlite3.connect(settings.database_path)

def init():
    connection = connect_db()
    connection.executescript(sql_schema.strip())
    connection.commit()

def create_task():
    connection = connect_db()
    connection.execute("insert into tasks (created) values (?)", [time.time()])
    connection.commit()
    task_id, = (connection
            .execute("select id from tasks order by created desc limit 1")
            .fetchone())
    return task_id

def finish_task(task_id, result):
    connection = connect_db()
    connection.execute(
            "update tasks set finished=?, result=? where id=?",
            [time.time(), result, task_id])
    connection.commit()

def get_task_result(task_id):
    return (connect_db()
            .execute("select finished, result from tasks where id=?", [task_id])
            .fetchone())

def get_all():
    return (connect_db()
            .execute("select * from tasks order by id asc")
            .fetchall())
