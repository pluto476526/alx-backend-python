import mysql.connector

def stream_users_in_batches(batch_size):
    """Generator that yields rows from user_data table in batches."""
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ALX_prodev"
    )
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_data")

    batch = []
    for row in cursor:
        batch.append(row)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch  # yield final incomplete batch

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """Generator that yields users over age 25, batch by batch."""
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                yield user

