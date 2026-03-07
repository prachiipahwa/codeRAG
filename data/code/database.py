import sqlite3

def connect_db():
    connection = sqlite3.connect("app.db")
    return connection

def get_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()

    conn.close()
    return user