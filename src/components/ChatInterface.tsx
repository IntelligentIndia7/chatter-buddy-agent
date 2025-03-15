
import React, { useState, useRef, useEffect } from 'react';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';
import { ArrowUp, Bot, User, RefreshCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useChatbot } from '@/hooks/use-chatbot';

type MessageRole = 'bot' | 'agent' | 'system';

interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
}

const ChatMessage: React.FC<{ message: Message }> = ({ message }) => {
  return (
    <div 
      className={cn(
        'p-4 rounded-lg my-2 animate-slide-in max-w-[85%]',
        message.role === 'bot' ? 'message-bot ml-auto' : 
        message.role === 'agent' ? 'message-agent mr-auto' : 'message-system mx-auto'
      )}
    >
      <div className="flex items-start gap-3">
        <Avatar className="h-8 w-8 mt-1">
          {message.role === 'bot' ? <Bot className="h-5 w-5" /> : 
           message.role === 'agent' ? <User className="h-5 w-5" /> : 
           <RefreshCcw className="h-5 w-5" />}
        </Avatar>
        <div>
          <p className="text-sm font-medium mb-1">
            {message.role === 'bot' ? 'Customer Bot' : 
             message.role === 'agent' ? 'Support Agent' : 'System'}
          </p>
          <p className="text-sm leading-relaxed">{message.content}</p>
          <p className="text-xs text-muted-foreground mt-2">
            {message.timestamp.toLocaleTimeString()}
          </p>
        </div>
      </div>
    </div>
  );
};

const TypingIndicator = () => {
  return (
    <div className="p-4 rounded-lg my-2 message-agent max-w-[60%] animate-pulse mr-auto">
      <div className="flex items-start gap-3">
        <Avatar className="h-8 w-8 mt-1">
          <User className="h-5 w-5" />
        </Avatar>
        <div>
          <p className="text-sm font-medium mb-1">Support Agent</p>
          <p className="text-sm typing-indicator">Typing</p>
        </div>
      </div>
    </div>
  );
};

const ChatInterface: React.FC = () => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  const { 
    messages, 
    isAgentTyping, 
    sendMessage, 
    resetChat,
    conversationState,
    isInitializing
  } = useChatbot();

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() === '') return;
    sendMessage(input);
    setInput('');
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isAgentTyping]);

  return (
    <Card className="glass relative flex flex-col h-[80vh] max-w-5xl mx-auto my-8 overflow-hidden border border-border/50">
      <div className="p-4 bg-secondary/30 backdrop-blur-sm border-b border-border/50">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">Customer Support Bot</h2>
          <Button variant="outline" size="sm" onClick={resetChat}>
            <RefreshCcw className="h-4 w-4 mr-2" /> Reset Chat
          </Button>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Current state: {isInitializing ? 'Initializing...' : conversationState}
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}
        {isAgentTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      <Separator />

      <form onSubmit={handleSendMessage} className="p-4 bg-secondary/10 backdrop-blur-xs">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1"
            disabled={isInitializing}
          />
          <Button type="submit" disabled={isInitializing || input.trim() === ''}>
            <ArrowUp className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default ChatInterface;
