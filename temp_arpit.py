from prettytable import PrettyTable
import sqlite3

x = PrettyTable()

# Connect to the database file
connection = sqlite3.connect('instance/database.db')
cursor = connection.cursor()

# Execute an SQL query
# cursor.execute("DELETE FROM User")
cursor.execute("SELECT * FROM User")

# Fetch all rows from the result set
rows = cursor.fetchall()

# Iterate through the rows and process the data
x.field_names = ["Sr No.", "Name", "Email"]
for id, name, email, hash in rows:
    x.add_row([id, name, email])

# Close the database connection
connection.close()
print(x)