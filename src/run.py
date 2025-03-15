
import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if GROQ_API_KEY is set
if not os.environ.get("GROQ_API_KEY"):
    print("Error: GROQ_API_KEY environment variable is not set.")
    print("Please add your Groq API key to the .env file or set it as an environment variable.")
    sys.exit(1)

# Run the Streamlit application
os.system("streamlit run src/app.py")
