
# Customer Support Bot Simulator

This application simulates a customer support interaction where an AI bot acts on behalf of a customer. The bot interacts with a support agent to inquire about insurance coverage.

## Features

- Automated conversation flow through different states using LangGraph
- Natural language processing with LangChain and Groq LLM
- Interactive chat interface built with Streamlit
- State tracking for meaningful conversations

## Setup

1. Create a `.env` file in the src directory with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```

2. Install the required packages:
   ```
   pip install -r src/requirements.txt
   ```

3. Run the application:
   ```
   python src/run.py
   ```

## Conversation Flow

1. Bot introduces itself and asks for agent's name
2. Bot confirms if it's in the right queue for coverage inquiries
3. Bot provides member ID for authentication
4. Bot inquires about plan status
5. Conversation concludes
