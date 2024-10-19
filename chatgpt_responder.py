from openai import OpenAI

class ChatGPTResponder:
    def __init__(self, api_key, db_manager):
        self.client = OpenAI(api_key=api_key)
        self.db_manager = db_manager
        self.qa_pairs = [
            {"question": "What is my current bill amount?", "answer": "Your current bill amount is {amount}, due on {due_date}."},
            {"question": "How can I pay my electric bill online?", "answer": "You can pay your bill online by logging into your account at www.electriccompany.com/pay. We accept credit cards, debit cards, and bank transfers."},
            {"question": "I'm experiencing a power outage in my neighborhood. What should I do?", "answer": "I'm sorry for the inconvenience. Please report the outage through our outage reporting page at www.electriccompany.com/outages or call our outage hotline at 1-800-555-1234. We are working to restore power as quickly as possible."},
            # Add all other Q&A pairs here...
        ]

    def get_response(self, user_input):
        customer_info = self.db_manager.get_customer_info(user_input)
        prompt = self._construct_prompt(user_input, customer_info)
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI assistant for an electric utility company. Answer the user's question based on the provided information and customer data."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def _construct_prompt(self, user_input, customer_info):
        qa_info = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in self.qa_pairs])
        customer_data = f"Customer ID: {customer_info['customer_id']}\nName: {customer_info['first_name']} {customer_info['last_name']}\nEmail: {customer_info['email']}\nPhone: {customer_info['phone']}\nAddress: {customer_info['address']}\nCurrent Bill: ${customer_info['current_bill']}\nDue Date: {customer_info['due_date']}\nLast Month's Usage: {customer_info['last_month_usage']} kWh"
        
        return f"""
Information:
{qa_info}

Customer Data:
{customer_data}

User Question: {user_input}

Please provide a response based on the above information and customer data. If the question isn't directly addressed in the provided information, use your general knowledge to give a helpful response, but prioritize the given information and customer data.
"""