
from database import get_connection

connection = get_connection()

if connection is not None:
    print("MySQL connected successfully!")

    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE()")

    print("Connected database:", cursor.fetchone()[0])

    cursor.close()
    connection.close()
else:
    print("Connection failed. Check your credentials.")
