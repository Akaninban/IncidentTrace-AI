
import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database="incidenttrace_db",
            connection_timeout=10
        )
        return connection

    except Error as error:
        print("MySQL connection failed:", error)
        return None


def save_search_history(user_id, question, response):
    """Save a user's question and AI response to MySQL."""

    connection = get_connection()

    if connection is None:
        print("Cannot save history: database connection failed.")
        return False

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO search_history
            (user_id, user_question, ai_response)
            VALUES (%s, %s, %s)
        """

        cursor.execute(query, (user_id, question, response))
        connection.commit()

        print("Search history saved successfully.")
        return True

    except Error as error:
        connection.rollback()
        print("Error saving search history:", error)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()
