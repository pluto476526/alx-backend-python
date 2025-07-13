import seed

def stream_user_ages():
    """Generator that yields user ages one by one from the user_data table."""
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data")

    for (age,) in cursor:
        yield age

    cursor.close()
    connection.close()


def compute_average_age():
    """Computes average age using the stream_user_ages generator."""
    total = 0
    count = 0
    for age in stream_user_ages():  # ✅ first loop
        total += age
        count += 1

    if count > 0:
        average = total / count
        print(f"Average age of users: {average:.2f}")
    else:
        print("No users found.")

