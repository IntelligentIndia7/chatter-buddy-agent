
import { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

type MessageRole = 'bot' | 'agent' | 'system';

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

type ConversationState = 
  | 'introduction' 
  | 'queue_verification' 
  | 'authentication' 
  | 'inquiry'
  | 'completed';

// Mock conversation data
const AGENT_RESPONSES = {
  introduction: [
    "Hello, thank you for calling customer support. My name is Alex. How can I help you today?",
    "Good day, you've reached customer support. I'm Jamie. How may I assist you?",
    "Welcome to customer support. This is Taylor speaking. What can I do for you today?"
  ],
  queue_verification: [
    "Yes, you're in the right queue for coverage inquiries. How can I help?",
    "Actually, this is the general support queue. Let me transfer you to the coverage department. Their direct number is 555-123-4567.",
    "You're in the right place. I can help you with your coverage questions."
  ],
  authentication: [
    "I'll need to verify your identity. Can you please provide your member ID?",
    "Thanks for the member ID. For security purposes, could you also confirm your date of birth?",
    "Perfect, I've verified your identity in our system. How can I help with your coverage today?"
  ],
  inquiry: [
    "I've checked your plan, and yes, it is currently active.",
    "Your plan is active and set to renew on the 15th of next month.",
    "I see that your plan is currently active. Your coverage includes medical, dental, and vision."
  ]
};

// Bot scripted responses based on conversation state
const BOT_SCRIPTS = {
  introduction: "Hello, I'm calling on behalf of John Doe. I'd like to inquire about his insurance coverage. May I know your name please?",
  queue_verification: (agentName: string) => `Thank you, ${agentName}. I want to confirm if I'm in the right queue to inquire about insurance coverage details?`,
  authentication: "I understand you need to verify the identity. The member ID is JD123456. Do you need any additional information to authenticate?",
  authentication_followup: "The date of birth is January 15, 1980.",
  inquiry: "Great, thank you for verifying. I'd like to know if the plan is currently active."
};

// Simulate typing delay for realistic responses
const getRandomDelay = () => Math.floor(Math.random() * 1000) + 1500;

export function useChatbot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationState, setConversationState] = useState<ConversationState>('introduction');
  const [isAgentTyping, setIsAgentTyping] = useState(false);
  const [agentName, setAgentName] = useState('');
  const [isRightQueue, setIsRightQueue] = useState(false);
  const [memberID, setMemberID] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);

  // Initialize the chat with a system message
  useEffect(() => {
    setTimeout(() => {
      setMessages([
        {
          id: uuidv4(),
          role: 'system',
          content: 'Customer support chat initialized. Bot will act on behalf of the customer.',
          timestamp: new Date()
        }
      ]);
      
      // Start the conversation
      setTimeout(() => {
        addMessage('bot', BOT_SCRIPTS.introduction);
        setIsInitializing(false);
      }, 1000);
    }, 1500);
  }, []);

  // Helper to add a message to the chat
  const addMessage = useCallback((role: MessageRole, content: string) => {
    setMessages(prev => [
      ...prev, 
      { 
        id: uuidv4(), 
        role, 
        content, 
        timestamp: new Date() 
      }
    ]);
  }, []);

  // Process agent response based on current state
  const processAgentResponse = useCallback((content: string) => {
    // Add agent's message to chat
    addMessage('agent', content);
    
    // Logic to progress conversation based on state
    switch(conversationState) {
      case 'introduction':
        // Try to extract name from agent's introduction
        const nameMatch = content.match(/name is (\w+)|(\w+) speaking/i);
        if (nameMatch) {
          const extractedName = nameMatch[1] || nameMatch[2];
          setAgentName(extractedName);
          
          // Move to next state
          setTimeout(() => {
            const nextMessage = BOT_SCRIPTS.queue_verification(extractedName);
            addMessage('bot', nextMessage);
            setConversationState('queue_verification');
          }, getRandomDelay());
        }
        break;
        
      case 'queue_verification':
        // Check if in the right queue
        const isCorrectQueue = content.toLowerCase().includes('right') || 
                               content.toLowerCase().includes('yes') || 
                               !content.toLowerCase().includes('transfer');
        setIsRightQueue(isCorrectQueue);
        
        if (isCorrectQueue) {
          // Proactively provide authentication info
          setTimeout(() => {
            addMessage('bot', BOT_SCRIPTS.authentication);
            setConversationState('authentication');
          }, getRandomDelay());
        } else {
          // Record transfer information
          const phoneNumberMatch = content.match(/\d{3}[-.\s]?\d{3}[-.\s]?\d{4}/);
          if (phoneNumberMatch) {
            const transferNumber = phoneNumberMatch[0];
            setTimeout(() => {
              addMessage('bot', `I'll call the coverage department at ${transferNumber}. Thank you for your assistance.`);
              setConversationState('completed');
            }, getRandomDelay());
          } else {
            setTimeout(() => {
              addMessage('bot', "Thank you for the information. I'll try to reach the correct department.");
              setConversationState('completed');
            }, getRandomDelay());
          }
        }
        break;
        
      case 'authentication':
        // Check if additional authentication is needed
        const needsMoreInfo = content.toLowerCase().includes('also') || 
                             content.toLowerCase().includes('additional') ||
                             content.toLowerCase().includes('date of birth');
        
        if (needsMoreInfo) {
          setTimeout(() => {
            addMessage('bot', BOT_SCRIPTS.authentication_followup);
          }, getRandomDelay());
        } else if (content.toLowerCase().includes('verified') || 
                  content.toLowerCase().includes('confirmed')) {
          setIsAuthenticated(true);
          setTimeout(() => {
            addMessage('bot', BOT_SCRIPTS.inquiry);
            setConversationState('inquiry');
          }, getRandomDelay());
        }
        break;
        
      case 'inquiry':
        // Process plan status information
        if (content.toLowerCase().includes('active')) {
          setTimeout(() => {
            addMessage('bot', "Thank you for confirming the plan is active. That's all I needed to know for now.");
            setConversationState('completed');
          }, getRandomDelay());
        }
        break;
        
      default:
        // Handle any other state
        break;
    }
  }, [conversationState, addMessage]);

  // Simulate an agent response
  const getAgentResponse = useCallback(() => {
    setIsAgentTyping(true);
    
    setTimeout(() => {
      const responses = AGENT_RESPONSES[conversationState];
      const randomResponse = responses[Math.floor(Math.random() * responses.length)];
      processAgentResponse(randomResponse);
      setIsAgentTyping(false);
    }, getRandomDelay());
  }, [conversationState, processAgentResponse]);

  // Handle sending a message
  const sendMessage = useCallback((content: string) => {
    // Add user's message
    addMessage('bot', content);
    
    // Get agent response
    getAgentResponse();
  }, [addMessage, getAgentResponse]);

  // Reset the chat
  const resetChat = useCallback(() => {
    setIsInitializing(true);
    setMessages([]);
    setConversationState('introduction');
    setAgentName('');
    setIsRightQueue(false);
    setMemberID('');
    setIsAuthenticated(false);
    
    // Add system message
    setTimeout(() => {
      setMessages([
        {
          id: uuidv4(),
          role: 'system',
          content: 'Chat reset. Starting new conversation.',
          timestamp: new Date()
        }
      ]);
      
      // Start the conversation
      setTimeout(() => {
        addMessage('bot', BOT_SCRIPTS.introduction);
        setIsInitializing(false);
      }, 1000);
    }, 1000);
  }, [addMessage]);

  return {
    messages,
    isAgentTyping,
    sendMessage,
    resetChat,
    conversationState,
    agentName,
    isRightQueue,
    isAuthenticated,
    isInitializing
  };
}
