from openai import OpenAI

class ChatGPTResponder:
    def __init__(self, api_key, db_manager):
        self.client = OpenAI(api_key=api_key)
        self.db_manager = db_manager
        self.utility_keywords = [
            "bill", "payment", "usage", "meter", "outage", "power", "electricity",
            "account", "service", "rate", "kilowatt", "kwh", "energy", "utility"
        ]
        self.conversation_history = []
        self.current_customer_id = None

    def start_new_conversation(self, customer_id):
        self.conversation_history = []
        self.current_customer_id = customer_id

    def end_conversation(self):
        if self.conversation_history:
            transcript = "\n".join([f"{'AI' if msg['role'] == 'assistant' else 'Customer'}: {msg['content']}" 
                                    for msg in self.conversation_history])
            self.db_manager.log_conversation(self.current_customer_id, transcript)
        self.conversation_history = []
        self.current_customer_id = None

    def get_response(self, user_input):
        customer_info = self.db_manager.get_customer_info(user_input)
        is_utility_related = self._is_utility_related(user_input)
        
        if not self.current_customer_id:
            self.start_new_conversation(customer_info['customer_id'] if customer_info else None)
        
        self.conversation_history.append({"role": "user", "content": user_input})
        
        system_prompt = self._get_system_prompt(is_utility_related)
        messages = [
            {"role": "system", "content": system_prompt},
            *self.conversation_history
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        ai_response = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response

    def _is_utility_related(self, user_input):
        return any(keyword in user_input.lower() for keyword in self.utility_keywords)

    def _get_system_prompt(self, is_utility_related):
        if is_utility_related:
            return ("You are an AI assistant for an electric utility company. "
                    "Answer the user's question based on the provided information and customer data. "
                    "If you can't provide a specific answer, suggest connecting the user with a human representative.")
        else:
            return ("You are an AI assistant for an electric utility company. "
                    "Engage in friendly conversation while being ready to assist with any utility-related queries.")

    def _construct_prompt(self, user_input, customer_info, is_utility_related):
        if customer_info:
            greeting = f"Hello {customer_info['first_name']} {customer_info['last_name']}! "
            customer_data = (f"Customer ID: {customer_info['customer_id']}\n"
                             f"Email: {customer_info['email']}\n"
                             f"Phone: {customer_info['phone']}\n"
                             f"Address: {customer_info['address']}\n"
                             f"Current Bill: ${customer_info['current_bill']}\n"
                             f"Due Date: {customer_info['due_date']}\n"
                             f"Last Month's Usage: {customer_info['last_month_usage']} kWh")
        else:
            greeting = "Hello! "
            customer_data = "No customer information found."

        if is_utility_related:
            return f"""
{greeting}It seems you have a question about your utility service.

Customer Data:
{customer_data}

User Question: {user_input}

Please provide a response based on the above information and customer data. If you can't provide a specific answer or if the query requires account-specific actions, suggest connecting the user with a human representative.
"""
        else:
            return f"""
{greeting}

User Input: {user_input}

Please engage in friendly conversation with the user. If they bring up any utility-related topics, offer to assist them or connect them with a representative if needed.
"""