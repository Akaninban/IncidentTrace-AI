
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_connection


def register_user(full_name, email, password):
    full_name = full_name.strip()
    email = email.strip().lower()

    if not full_name or not email or not password:
        return False, "Please fill in all fields."

    if len(password) < 8:
        return False, "Password must be at least 8 characters."

    connection = get_connection()
    if connection is None:
        return False, "Database connection failed."

    cursor = None
    try:
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,)
        )

        if cursor.fetchone():
            return False, "Email is already registered."

        password_hash = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash)
        )

        connection.commit()
        return True, "Registration successful. Please log in."

    except Exception as error:
        connection.rollback()
        print("Registration error:", error)
        return False, "Registration failed."

    finally:
        if cursor:
            cursor.close()
        connection.close()


def login_user(email, password):
    connection = get_connection()
    if connection is None:
        return None, "Database connection failed."

    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, full_name, email, password_hash
            FROM users
            WHERE email = %s
            """,
            (email.strip().lower(),)
        )

        user = cursor.fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            user.pop("password_hash", None)
            return user, "Login successful."

        return None, "Incorrect email or password."

    except Exception as error:
        print("Login error:", error)
        return None, "Login failed."

    finally:
        if cursor:
            cursor.close()
        connection.close()
