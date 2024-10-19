import mysql.connector
from mysql.connector import Error
import os
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.connection = None
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD")
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
                self.create_conversation_log_table()
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def create_conversation_log_table(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_id INT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    transcript TEXT,
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """)
            self.connection.commit()
            cursor.close()
            print("conversation_logs table created or already exists")
        except Error as e:
            print(f"Error creating conversation_logs table: {e}")

    def log_conversation(self, customer_id, transcript):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO conversation_logs (customer_id, transcript) VALUES (%s, %s)"
            cursor.execute(query, (customer_id, transcript))
            self.connection.commit()
            cursor.close()
            print("Conversation logged successfully")
        except Error as e:
            print(f"Error logging conversation: {e}")

    def get_customer_info(self, user_input):
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Extract potential identifiers from user input
            name_match = re.search(r'name is (\w+(\s\w+)?)', user_input, re.IGNORECASE)
            phone_match = re.search(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{10})', user_input)
            email_match = re.search(r'[\w\.-]+@[\w\.-]+', user_input)

            customer = None

            if name_match:
                full_name = name_match.group(1).split()
                if len(full_name) > 1:
                    cursor.execute("""
                        SELECT * FROM customers 
                        WHERE LOWER(first_name) = LOWER(%s) AND LOWER(last_name) = LOWER(%s)
                    """, (full_name[0], full_name[-1]))
                else:
                    cursor.execute("""
                        SELECT * FROM customers 
                        WHERE LOWER(first_name) = LOWER(%s) OR LOWER(last_name) = LOWER(%s)
                    """, (full_name[0], full_name[0]))
                customer = cursor.fetchone()

            if not customer and phone_match:
                phone = re.sub(r'\D', '', phone_match.group())  # Remove non-digit characters
                cursor.execute("SELECT * FROM customers WHERE phone = %s", (phone,))
                customer = cursor.fetchone()

            if not customer and email_match:
                email = email_match.group()
                cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
                customer = cursor.fetchone()

            if not customer:
                print("Customer not found.")
                return {}

            # Get latest bill
            cursor.execute("""
                SELECT * FROM bills 
                WHERE customer_id = %s 
                ORDER BY bill_date DESC 
                LIMIT 1
            """, (customer['customer_id'],))
            bill = cursor.fetchone()

            # Get last month's usage
            cursor.execute("""
                SELECT kwh_used FROM power_usage 
                WHERE customer_id = %s 
                ORDER BY usage_date DESC 
                LIMIT 1
            """, (customer['customer_id'],))
            usage = cursor.fetchone()

            cursor.close()

            return {
                'customer_id': customer['customer_id'],
                'first_name': customer['first_name'],
                'last_name': customer['last_name'],
                'email': customer['email'],
                'phone': customer['phone'],
                'address': customer['address'],
                'current_bill': bill['amount'] if bill else None,
                'due_date': bill['due_date'] if bill else None,
                'last_month_usage': usage['kwh_used'] if usage else None
            }
        except Error as e:
            print(f"Error while querying database: {e}")
            return {}