
user = input("name: ")
query = "SELECT * FROM products WHERE name = '" + user + "'"
cursor.execute(query)
