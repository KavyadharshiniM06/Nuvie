import mysql.connector;
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="MovieRecommendationDB"
)

cursor = conn.cursor()
#insert_query = "INSERT INTO users (user_id, username, email, password_hash, created_at) VALUES (%s, %s, %s, %s, NOW())"
#values = (2, 'kavya', 'kavya@example.com', 'password!')

#cursor.execute(insert_query, values)

#conn.commit()  # Commit the transaction

#print("Record inserted successfully!")

cursor.execute("SELECT * FROM users")

# Fetch all records
records = cursor.fetchall()

# Display the records
print("Records in the table:")
for row in records:
    print(row)
# Close the connection
cursor.close()
conn.close()