
import streamlit as st
from bot_agent import handle_agent_input

# Set page config
st.set_page_config(
    page_title="Customer Support Bot Simulator",
    page_icon="🤖",
    layout="centered"
)

# Add custom styling
st.markdown("""
<style>
    .main {
        background-color: #f9fafc;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 0.75rem;
    }
    .chat-message.bot {
        background-color: #e6f7ff;
        border-left: 5px solid #1890ff;
    }
    .chat-message.agent {
        background-color: #f0f0f0;
        border-left: 5px solid #595959;
    }
    .chat-message .avatar {
        min-width: 36px;
        min-height: 36px;
        border-radius: 50%;
        background-color: #fff;
        display: flex;
        justify-content: center;
        align-items: center;
        font-weight: bold;
        font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chat-message .content {
        width: 100%;
    }
    .chat-message .content .sender {
        font-weight: bold;
        margin-bottom: 0.25rem;
    }
    .chat-message .content .message {
        line-height: 1.5;
    }
    .chat-info {
        background-color: #fffbe6;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 5px solid #faad14;
        margin-bottom: 1rem;
    }
    .state-info {
        background-color: #f6ffed;
        padding: 0.75rem;
        border-radius: 0.5rem;
        border-left: 5px solid #52c41a;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "state" not in st.session_state:
    st.session_state.state = {
        "messages": [],
        "agent_name": None,
        "member_id": None,
        "correct_queue": None,
        "authenticated": None,
        "plan_status": None,
        "conversation_state": "INTRODUCTION"
    }
    
    # Trigger initial bot message
    updated_state = handle_agent_input("Hello, this is customer support. How can I help you today?", st.session_state.state)
    st.session_state.state = updated_state
    
    # Add messages to session state
    for msg in updated_state["messages"]:
        if msg["role"] == "agent":
            st.session_state.messages.append({"role": "agent", "content": msg["content"]})
        elif msg["role"] == "bot":
            st.session_state.messages.append({"role": "bot", "content": msg["content"]})

# App title
st.title("Customer Support Bot Simulator")

# App description
st.markdown("""
This application simulates a customer support interaction where an AI bot acts on behalf of a customer.
The bot will interact with you (acting as the support agent) to inquire about insurance coverage.
""")

# Display information card
with st.container():
    st.markdown("""
    <div class="chat-info">
        <b>Conversation Flow:</b>
        <ol>
            <li>Bot introduces itself and asks for agent's name</li>
            <li>Bot confirms if it's in the right queue for coverage inquiries</li>
            <li>Bot provides member ID for authentication</li>
            <li>Bot inquires about plan status</li>
            <li>Conversation concludes</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
st.subheader("Chat")
for msg in st.session_state.messages:
    if msg["role"] == "agent":
        st.markdown(f"""
        <div class="chat-message agent">
            <div class="avatar">A</div>
            <div class="content">
                <div class="sender">Support Agent</div>
                <div class="message">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message bot">
            <div class="avatar">C</div>
            <div class="content">
                <div class="sender">Customer Bot</div>
                <div class="message">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Input for agent response
agent_input = st.chat_input("Type your agent response...")

if agent_input:
    # Add agent message to chat
    st.session_state.messages.append({"role": "agent", "content": agent_input})
    
    # Process with bot
    updated_state = handle_agent_input(agent_input, st.session_state.state)
    st.session_state.state = updated_state
    
    # Get bot's response and add to chat
    if len(updated_state["messages"]) > 0 and updated_state["messages"][-1]["role"] == "bot":
        bot_response = updated_state["messages"][-1]["content"]
        st.session_state.messages.append({"role": "bot", "content": bot_response})
    
    # Force a rerun to update the UI
    st.rerun()

# Show current state (for debugging)
with st.expander("Current Conversation State"):
    st.markdown(f"""
    <div class="state-info">
        <p><b>Current state:</b> {st.session_state.state["conversation_state"]}</p>
        <p><b>Agent name:</b> {st.session_state.state["agent_name"] or "Not identified yet"}</p>
        <p><b>Correct queue:</b> {str(st.session_state.state["correct_queue"]) if st.session_state.state["correct_queue"] is not None else "Not confirmed yet"}</p>
        <p><b>Member ID:</b> {st.session_state.state["member_id"] or "Not provided yet"}</p>
        <p><b>Authentication status:</b> {str(st.session_state.state["authenticated"]) if st.session_state.state["authenticated"] is not None else "Not authenticated yet"}</p>
        <p><b>Plan status:</b> {st.session_state.state["plan_status"] or "Not inquired yet"}</p>
    </div>
    """, unsafe_allow_html=True)

# Reset conversation button
if st.button("Reset Conversation"):
    st.session_state.messages = []
    st.session_state.state = {
        "messages": [],
        "agent_name": None,
        "member_id": None,
        "correct_queue": None,
        "authenticated": None,
        "plan_status": None,
        "conversation_state": "INTRODUCTION"
    }
    
    # Trigger initial bot message
    updated_state = handle_agent_input("Hello, this is customer support. How can I help you today?", st.session_state.state)
    st.session_state.state = updated_state
    
    # Add messages to session state
    for msg in updated_state["messages"]:
        if msg["role"] == "agent":
            st.session_state.messages.append({"role": "agent", "content": msg["content"]})
        elif msg["role"] == "bot":
            st.session_state.messages.append({"role": "bot", "content": msg["content"]})
    
    st.rerun()
