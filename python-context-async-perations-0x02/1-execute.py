#!/usr/bin/env python3
"""
Reusable context manager that handles MySQL database connection and query execution.
"""

import mysql.connector


class ExecuteQuery:
    def __init__(self, host, user, password, database, query, params=None):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }
        self.query = query
        self.params = params
        self.conn = None
        self.cursor = None
        self.results = None

    def __enter__(self):
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.results = self.cursor.fetchall()
        return self.results

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    host = "localhost"
    user = "root"
    password = ""
    database = "alx_db"

    query = "SELECT * FROM users WHERE age > %s"
    params = (25,)

    with ExecuteQuery(host, user, password, database, query, params) as results:
        for row in results:
            print(row)

