
# Customer Support Bot Simulator

A Python-based Streamlit application that simulates a customer support interaction with an AI bot acting on behalf of a customer.

## Setup Instructions

1. Clone this repository
2. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   python run.py
   ```

## About This Project

This application uses:
- Streamlit for the UI
- LangChain and LangGraph for the conversation flow
- Groq for LLM access

The customer bot follows a specific conversation flow:
1. Introduction and asking for the agent's name
2. Confirmation of being in the correct queue for coverage inquiries
3. Authentication with a member ID
4. Inquiry about insurance plan status
5. Conclusion of the conversation
