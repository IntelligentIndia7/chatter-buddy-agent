
import os
from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from datetime import datetime

# Initialize the LLM
llm = ChatGroq(
    model_name="llama3-70b-8192",
    api_key=os.environ.get("GROQ_API_KEY")
)

# Define conversation states
CONVERSATION_STATES = {
    "INTRODUCTION": "Introduction phase where the bot introduces itself",
    "QUEUE_CONFIRMATION": "Confirming if this is the right queue for coverage inquiries",
    "AUTHENTICATION": "Authenticating the member using their ID",
    "PLAN_INQUIRY": "Inquiring about the plan status",
    "CONCLUSION": "Concluding the conversation"
}

# Define the state schema
class CustomerState:
    messages: List[Dict[str, str]]
    agent_name: Optional[str]
    member_id: Optional[str]
    correct_queue: Optional[bool]
    authenticated: Optional[bool]
    plan_status: Optional[str]
    conversation_state: str

# Define the nodes for the conversation graph
def determine_next_state(state: Dict[str, Any]) -> str:
    """Determine the next state of the conversation based on current state and responses."""
    current_state = state.get("conversation_state", "INTRODUCTION")
    
    if current_state == "INTRODUCTION":
        if state.get("agent_name"):
            return "QUEUE_CONFIRMATION"
        return "INTRODUCTION"
    
    elif current_state == "QUEUE_CONFIRMATION":
        if state.get("correct_queue") is not None:
            return "AUTHENTICATION"
        return "QUEUE_CONFIRMATION"
    
    elif current_state == "AUTHENTICATION":
        if state.get("authenticated"):
            return "PLAN_INQUIRY"
        return "AUTHENTICATION"
    
    elif current_state == "PLAN_INQUIRY":
        if state.get("plan_status"):
            return "CONCLUSION"
        return "PLAN_INQUIRY"
    
    elif current_state == "CONCLUSION":
        return END
    
    return current_state

def introduction(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the introduction phase of the conversation."""
    # Extract the most recent agent message
    agent_messages = [m for m in state["messages"] if m["role"] == "agent"]
    
    if not agent_messages:
        # If no agent messages yet, this is the initial state
        return state
    
    recent_agent_msg = agent_messages[-1]["content"]
    
    # Check if the agent has introduced themselves
    agent_name = None
    
    # Simple name extraction logic
    if "name is" in recent_agent_msg.lower():
        name_part = recent_agent_msg.lower().split("name is")[1].strip()
        agent_name = name_part.split()[0].capitalize()
    elif "this is" in recent_agent_msg.lower():
        name_part = recent_agent_msg.lower().split("this is")[1].strip()
        agent_name = name_part.split()[0].capitalize()
    
    if agent_name:
        # Update state with agent name
        state["agent_name"] = agent_name
        
        # Add bot response thanking agent and asking about queue
        bot_response = f"Nice to meet you, {agent_name}! My name is Sarah Johnson. I'm calling to check if my insurance covers a procedure I'm planning. Is this the right department for coverage inquiries?"
        
        # Add message to history
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update conversation state
        state["conversation_state"] = "QUEUE_CONFIRMATION"
    else:
        # If no name found, ask again
        bot_response = "I'm sorry, I didn't catch your name. Could you please tell me your name?"
        
        # Add message to history
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def queue_confirmation(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle confirming if this is the right queue for coverage inquiries."""
    agent_messages = [m for m in state["messages"] if m["role"] == "agent"]
    recent_agent_msg = agent_messages[-1]["content"].lower()
    
    # Check if response indicates this is the right queue
    positive_indicators = ["yes", "correct", "right", "can help", "assist you", "coverage"]
    negative_indicators = ["no", "wrong", "different", "not the right", "transfer"]
    
    is_correct_queue = None
    
    for indicator in positive_indicators:
        if indicator in recent_agent_msg:
            is_correct_queue = True
            break
    
    if is_correct_queue is None:
        for indicator in negative_indicators:
            if indicator in recent_agent_msg:
                is_correct_queue = False
                break
    
    if is_correct_queue is not None:
        state["correct_queue"] = is_correct_queue
        
        if is_correct_queue:
            # Provide member ID for authentication
            bot_response = "Great! My member ID is MEM123456789. Could you please verify my coverage?"
            state["member_id"] = "MEM123456789"
            state["conversation_state"] = "AUTHENTICATION"
        else:
            # Handle wrong queue
            bot_response = "Oh, I see. Could you please transfer me to the right department for coverage inquiries?"
            state["conversation_state"] = "CONCLUSION"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Unclear response, ask again
        bot_response = "I'm not sure if I'm in the right place. I need to check if my insurance covers a specific procedure. Can you help with coverage inquiries?"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def authentication(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the authentication phase."""
    agent_messages = [m for m in state["messages"] if m["role"] == "agent"]
    recent_agent_msg = agent_messages[-1]["content"].lower()
    
    # Check if authentication was successful
    positive_indicators = ["verified", "confirmed", "authenticated", "found you", "found your", "located your"]
    negative_indicators = ["not found", "can't find", "cannot find", "invalid", "incorrect"]
    
    is_authenticated = None
    
    for indicator in positive_indicators:
        if indicator in recent_agent_msg:
            is_authenticated = True
            break
    
    if is_authenticated is None:
        for indicator in negative_indicators:
            if indicator in recent_agent_msg:
                is_authenticated = False
                break
    
    if is_authenticated is not None:
        state["authenticated"] = is_authenticated
        
        if is_authenticated:
            # Ask about coverage for a specific procedure
            bot_response = "Thank you for verifying my account. I'm planning to have a routine colonoscopy next month. Does my current plan cover this procedure?"
            state["conversation_state"] = "PLAN_INQUIRY"
        else:
            # Handle failed authentication
            bot_response = "I'm sorry to hear that. Let me double-check my ID. Actually, I might need to call back later with the correct information."
            state["conversation_state"] = "CONCLUSION"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    else:
        # Need more info for authentication
        bot_response = "I provided my member ID MEM123456789. Do you need any additional information to verify my account?"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def plan_inquiry(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the plan inquiry phase."""
    agent_messages = [m for m in state["messages"] if m["role"] == "agent"]
    recent_agent_msg = agent_messages[-1]["content"].lower()
    
    # Analyze response about coverage
    covered_indicators = ["covered", "included", "part of your plan", "your plan covers"]
    not_covered_indicators = ["not covered", "isn't covered", "does not cover", "doesn't cover", "excluded"]
    
    plan_status = None
    
    for indicator in covered_indicators:
        if indicator in recent_agent_msg:
            plan_status = "Covered"
            break
    
    if plan_status is None:
        for indicator in not_covered_indicators:
            if indicator in recent_agent_msg:
                plan_status = "Not covered"
                break
    
    if plan_status:
        state["plan_status"] = plan_status
        
        if plan_status == "Covered":
            bot_response = "That's great news! Thank you for checking. Is there any paperwork I need to complete before the procedure?"
        else:
            bot_response = "I see. That's disappointing. Are there any alternative options or ways to get this covered?"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # We'll transition to conclusion after this
        state["conversation_state"] = "CONCLUSION"
    else:
        # Unclear response about coverage
        bot_response = "I'm not sure I understood whether the colonoscopy procedure is covered under my plan. Could you please clarify?"
        
        state["messages"].append({
            "role": "bot",
            "content": bot_response,
            "timestamp": datetime.now().isoformat()
        })
    
    return state

def conclusion(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the conclusion of the conversation."""
    agent_messages = [m for m in state["messages"] if m["role"] == "agent"]
    recent_agent_msg = agent_messages[-1]["content"]
    
    # Generate a conclusion based on the conversation history
    agent_name = state.get("agent_name", "support agent")
    
    bot_response = f"Thank you so much for your help today, {agent_name}! You've been very informative. Have a great day!"
    
    state["messages"].append({
        "role": "bot",
        "content": bot_response,
        "timestamp": datetime.now().isoformat()
    })
    
    return state

def handle_agent_input(agent_input: str, current_state: Dict[str, Any]) -> Dict[str, Any]:
    """Main function to handle agent input and update conversation state."""
    # Initialize state if needed
    if "messages" not in current_state:
        current_state = {
            "messages": [],
            "agent_name": None,
            "member_id": None,
            "correct_queue": None,
            "authenticated": None,
            "plan_status": None,
            "conversation_state": "INTRODUCTION"
        }
    
    # Add agent message to history
    current_state["messages"].append({
        "role": "agent",
        "content": agent_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # If this is the first message, respond with introduction
    if len(current_state["messages"]) == 1:
        current_state["messages"].append({
            "role": "bot",
            "content": "Hello! My name is Sarah Johnson, and I'm calling to inquire about my insurance coverage. May I ask who I'm speaking with?",
            "timestamp": datetime.now().isoformat()
        })
        return current_state
    
    # Create the conversation workflow graph
    workflow = StateGraph(CustomerState)
    
    # Add nodes to the graph
    workflow.add_node("INTRODUCTION", introduction)
    workflow.add_node("QUEUE_CONFIRMATION", queue_confirmation)
    workflow.add_node("AUTHENTICATION", authentication)
    workflow.add_node("PLAN_INQUIRY", plan_inquiry)
    workflow.add_node("CONCLUSION", conclusion)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "INTRODUCTION",
        determine_next_state,
        {
            "INTRODUCTION": "INTRODUCTION",
            "QUEUE_CONFIRMATION": "QUEUE_CONFIRMATION"
        }
    )
    
    workflow.add_conditional_edges(
        "QUEUE_CONFIRMATION",
        determine_next_state,
        {
            "QUEUE_CONFIRMATION": "QUEUE_CONFIRMATION",
            "AUTHENTICATION": "AUTHENTICATION",
            "CONCLUSION": "CONCLUSION"
        }
    )
    
    workflow.add_conditional_edges(
        "AUTHENTICATION",
        determine_next_state,
        {
            "AUTHENTICATION": "AUTHENTICATION",
            "PLAN_INQUIRY": "PLAN_INQUIRY",
            "CONCLUSION": "CONCLUSION"
        }
    )
    
    workflow.add_conditional_edges(
        "PLAN_INQUIRY",
        determine_next_state,
        {
            "PLAN_INQUIRY": "PLAN_INQUIRY",
            "CONCLUSION": "CONCLUSION"
        }
    )
    
    workflow.add_edge("CONCLUSION", END)
    
    # Set the entry point
    workflow.set_entry_point(current_state["conversation_state"])
    
    # Compile the graph
    app = workflow.compile()
    
    # Run the graph
    for output in app.stream(current_state):
        if "CONCLUSION" in output:
            final_state = output["CONCLUSION"]
            break
        elif END in output:
            final_state = output[END]
            break
        else:
            for key, value in output.items():
                if key in CONVERSATION_STATES:
                    final_state = value
    
    return final_state
