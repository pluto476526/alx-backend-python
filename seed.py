import mysql.connector
import csv
import uuid
from decimal import Decimal


def connect_db():
    """Connects to the MySQL server."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    """Creates the ALX_prodev database if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        connection.commit()
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Database creation error: {err}")


def connect_to_prodev():
    """Connects to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_table(connection):
    """Creates the user_data table if it does not exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL NOT NULL,
                INDEX (user_id)
            )
        """)
        connection.commit()
        cursor.close()
        print("Table user_data created successfully")
    except mysql.connector.Error as err:
        print(f"Table creation error: {err}")


def insert_data(connection, csv_file):
    """Inserts data from a CSV file into the user_data table."""
    try:
        cursor = connection.cursor()
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = row.get("user_id") or str(uuid.uuid4())
                name = row["name"]
                email = row["email"]
                age = Decimal(row["age"])
                cursor.execute("""
                    INSERT IGNORE INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, name, email, age))
        connection.commit()
        cursor.close()
        print("Data inserted successfully")
    except Exception as e:
        print(f"Data insertion error: {e}")


def stream_user_data(connection):
    """Generator that yields rows from user_data table one at a time."""
    try:
        cursor = connection.cursor(buffered=False)
        cursor.execute("SELECT * FROM user_data")

        while True:
            row = cursor.fetchone()
            if row is None:
                break
            yield row

        cursor.close()
    except mysql.connector.Error as err:
        print(f"Streaming error: {err}")

