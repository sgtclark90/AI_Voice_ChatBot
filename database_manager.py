import mysql.connector
from mysql.connector import Error
import os
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
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")

    def get_customer_info(self, user_input):
        # This is a simplified example. In a real scenario, you'd need to
        # extract customer identifiers from the user_input.
        customer_id = 1  # Placeholder, replace with actual logic to get customer_id
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            # Get customer details
            cursor.execute("""
                SELECT * FROM customers WHERE customer_id = %s
            """, (customer_id,))
            customer = cursor.fetchone()
            
            # Get latest bill
            cursor.execute("""
                SELECT * FROM bills 
                WHERE customer_id = %s 
                ORDER BY bill_date DESC 
                LIMIT 1
            """, (customer_id,))
            bill = cursor.fetchone()
            
            # Get last month's usage
            cursor.execute("""
                SELECT kwh_used FROM power_usage 
                WHERE customer_id = %s 
                ORDER BY usage_date DESC 
                LIMIT 1
            """, (customer_id,))
            usage = cursor.fetchone()
            
            cursor.close()
            
            return {
                'customer_id': customer['customer_id'],
                'first_name': customer['first_name'],
                'last_name': customer['last_name'],
                'email': customer['email'],
                'phone': customer['phone'],
                'address': customer['address'],
                'current_bill': bill['amount'],
                'due_date': bill['due_date'],
                'last_month_usage': usage['kwh_used']
            }
        except Error as e:
            print(f"Error while querying database: {e}")
            return {}

    def __del__(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")