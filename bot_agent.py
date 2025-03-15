
import os
from typing import Dict, List, Optional, TypedDict, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

# Define conversation states
ConversationState = Literal[
    "INTRODUCTION", 
    "QUEUE_CONFIRMATION", 
    "AUTHENTICATION", 
    "PLAN_INQUIRY",
    "CONCLUSION"
]

# Define the state schema
class State(TypedDict):
    messages: List[Dict]
    agent_name: Optional[str]
    member_id: Optional[str]
    correct_queue: Optional[bool]
    authenticated: Optional[bool]
    plan_status: Optional[str]
    conversation_state: ConversationState

# Initialize LLM
groq_api_key = os.environ.get("GROQ_API_KEY", "")
llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.7,
    api_key=groq_api_key
)

# System prompts for each state
SYSTEM_PROMPTS = {
    "INTRODUCTION": """You are a bot acting on behalf of a customer interacting with a customer support agent.
    Your goal is to introduce yourself politely and ask for the agent's name.
    Record the agent's name when they provide it.
    Only respond as the customer.""",
    
    "QUEUE_CONFIRMATION": """You are a bot acting on behalf of a customer.
    Your goal is to confirm if you're in the right queue for coverage inquiries.
    If not, ask to be transferred to the right queue or request the phone number for the right department.
    Remember the agent's name is {agent_name}.
    Only respond as the customer.""",
    
    "AUTHENTICATION": """You are a bot acting on behalf of a customer.
    Your goal is to provide authentication details.
    Offer your member ID (AD78902145) proactively and ask if any further details are needed.
    Remember the agent's name is {agent_name}.
    Only respond as the customer.""",
    
    "PLAN_INQUIRY": """You are a bot acting on behalf of a customer.
    Your goal is to inquire about whether your insurance plan is active.
    Ask {agent_name} to check if your plan is currently active.
    Only respond as the customer."""
}

# Define state transitions
def should_transition_to_queue_confirmation(state: State) -> bool:
    """Check if we should move to queue confirmation state"""
    messages = state["messages"]
    if len(messages) < 2:
        return False
    # After introducing and getting agent's name
    return state["agent_name"] is not None

def should_transition_to_authentication(state: State) -> bool:
    """Check if we should move to authentication state"""
    return state["correct_queue"] is True

def should_transition_to_plan_inquiry(state: State) -> bool:
    """Check if we should move to plan inquiry state"""
    return state["authenticated"] is True

def should_end_conversation(state: State) -> bool:
    """Check if we should end the conversation"""
    return state["plan_status"] is not None

# Define state processing functions
def process_introduction(state: State) -> State:
    """Process introduction state and extract agent name"""
    messages = state["messages"]
    # Check last message for agent name
    if len(messages) > 0 and messages[-1]["role"] == "agent":
        agent_message = messages[-1]["content"].lower()
        
        # Simple name extraction logic - can be improved with NER
        name_indicators = ["name is", "this is", "speaking", "i am", "i'm"]
        for indicator in name_indicators:
            if indicator in agent_message:
                parts = agent_message.split(indicator, 1)
                if len(parts) > 1:
                    # Take the first word after the indicator as the name
                    potential_name = parts[1].strip().split()[0].strip(',.!?')
                    if potential_name and len(potential_name) > 1:  # Ensure it's not just a letter
                        # Capitalize the name
                        state["agent_name"] = potential_name.capitalize()
                        break
    
    # Generate customer bot response
    system_prompt = SYSTEM_PROMPTS["INTRODUCTION"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate the customer's next response.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    
    # Add bot response to messages
    state["messages"].append({"role": "bot", "content": response})
    state["conversation_state"] = "INTRODUCTION"
    
    return state

def process_queue_confirmation(state: State) -> State:
    """Process queue confirmation state"""
    messages = state["messages"]
    
    # Check last agent message for queue confirmation
    if len(messages) > 0 and messages[-1]["role"] == "agent":
        agent_message = messages[-1]["content"].lower()
        
        # Check if agent confirmed correct queue
        if any(phrase in agent_message for phrase in ["coverage", "right queue", "correct queue", "help with coverage", "assist with coverage"]):
            state["correct_queue"] = True
        elif any(phrase in agent_message for phrase in ["wrong queue", "incorrect queue", "transfer you", "different department"]):
            state["correct_queue"] = False
    
    # Generate customer bot response
    system_prompt = SYSTEM_PROMPTS["QUEUE_CONFIRMATION"].format(agent_name=state["agent_name"] or "agent")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate the customer's next response.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    
    # Add bot response to messages
    state["messages"].append({"role": "bot", "content": response})
    state["conversation_state"] = "QUEUE_CONFIRMATION"
    
    return state

def process_authentication(state: State) -> State:
    """Process authentication state"""
    messages = state["messages"]
    
    # Check last agent message for authentication confirmation
    if len(messages) > 0 and messages[-1]["role"] == "agent":
        agent_message = messages[-1]["content"].lower()
        
        # Check if agent confirmed authentication
        if any(phrase in agent_message for phrase in ["authenticated", "verified", "confirmed your identity", "thank you for the information"]):
            state["authenticated"] = True
            state["member_id"] = "AD78902145"  # Store the member ID
    
    # Generate customer bot response
    system_prompt = SYSTEM_PROMPTS["AUTHENTICATION"].format(agent_name=state["agent_name"] or "agent")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate the customer's next response.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    
    # Add bot response to messages
    state["messages"].append({"role": "bot", "content": response})
    state["conversation_state"] = "AUTHENTICATION"
    
    return state

def process_plan_inquiry(state: State) -> State:
    """Process plan inquiry state"""
    messages = state["messages"]
    
    # Check last agent message for plan status information
    if len(messages) > 0 and messages[-1]["role"] == "agent":
        agent_message = messages[-1]["content"].lower()
        
        # Extract plan status
        if "active" in agent_message:
            state["plan_status"] = "active"
        elif "inactive" in agent_message or "not active" in agent_message or "expired" in agent_message:
            state["plan_status"] = "inactive"
    
    # Generate customer bot response
    system_prompt = SYSTEM_PROMPTS["PLAN_INQUIRY"].format(agent_name=state["agent_name"] or "agent")
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Generate the customer's next response.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({})
    
    # Add bot response to messages
    state["messages"].append({"role": "bot", "content": response})
    state["conversation_state"] = "PLAN_INQUIRY"
    
    return state

# Create the graph
def create_workflow() -> StateGraph:
    """Create the conversation workflow graph"""
    # Initialize the graph
    workflow = StateGraph(State)
    
    # Define nodes
    workflow.add_node("introduction", process_introduction)
    workflow.add_node("queue_confirmation", process_queue_confirmation)
    workflow.add_node("authentication", process_authentication)
    workflow.add_node("plan_inquiry", process_plan_inquiry)
    
    # Define edges
    workflow.add_edge("introduction", "queue_confirmation", should_transition_to_queue_confirmation)
    workflow.add_edge("queue_confirmation", "authentication", should_transition_to_authentication)
    workflow.add_edge("authentication", "plan_inquiry", should_transition_to_authentication)
    workflow.add_edge("plan_inquiry", END, should_end_conversation)
    
    # Add conditional loopbacks for states that need more interaction
    workflow.add_conditional_edges(
        "introduction",
        lambda state: "queue_confirmation" if should_transition_to_queue_confirmation(state) else "introduction"
    )
    workflow.add_conditional_edges(
        "queue_confirmation",
        lambda state: "authentication" if should_transition_to_authentication(state) else "queue_confirmation"
    )
    workflow.add_conditional_edges(
        "authentication",
        lambda state: "plan_inquiry" if should_transition_to_plan_inquiry(state) else "authentication"
    )
    workflow.add_conditional_edges(
        "plan_inquiry",
        lambda state: END if should_end_conversation(state) else "plan_inquiry"
    )
    
    # Set the entry point
    workflow.set_entry_point("introduction")
    
    return workflow

# Compile the graph
def get_customer_bot():
    """Get the compiled customer support bot workflow"""
    workflow = create_workflow()
    return workflow.compile()

# Function to handle agent input and generate bot response
def handle_agent_input(agent_input: str, state: Dict = None) -> Dict:
    """Process agent input and update conversation state"""
    if state is None:
        # Initialize state
        state = {
            "messages": [],
            "agent_name": None,
            "member_id": None,
            "correct_queue": None,
            "authenticated": None,
            "plan_status": None,
            "conversation_state": "INTRODUCTION"
        }
    
    # Add agent message to state
    state["messages"].append({"role": "agent", "content": agent_input})
    
    # Get the workflow
    customer_bot = get_customer_bot()
    
    # Process the state through the workflow
    for output in customer_bot.stream(state):
        if "messages" in output:
            latest_state = output
    
    return latest_state
