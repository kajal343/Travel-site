import sqlite3
from prettytable import from_db_cursor

connection = sqlite3.connect("instance/database.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM User")
mytable = from_db_cursor(cursor)


print(mytable)