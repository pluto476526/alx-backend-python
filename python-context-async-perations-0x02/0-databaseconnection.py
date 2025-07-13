#!/usr/bin/env python3
"""
Handles automatic MySQL database connection management using a class-based context manager.
"""

import mysql.connector


class DatabaseConnection:
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": ,
            "database": alx_db
        }
        self.conn = None

    def __enter__(self):
        self.conn = mysql.connector.connect(**self.config)
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    # Replace these credentials with your actual MySQL server details
    host = "localhost"
    user = "your_username"
    password = "your_password"
    database = "your_database"

    with DatabaseConnection(host, user, password, database) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        for row in results:
            print(row)

