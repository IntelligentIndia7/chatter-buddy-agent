
import React from 'react';
import ChatInterface from '@/components/ChatInterface';
import AnimatedBackground from '@/components/AnimatedBackground';
import { Card } from '@/components/ui/card';

const Index = () => {
  return (
    <div className="min-h-screen w-full">
      <AnimatedBackground />
      
      <div className="container px-4 py-8 relative z-10">
        <header className="text-center mb-10">
          <div className="inline-block mb-3">
            <span className="px-3 py-1 bg-primary/10 text-primary text-sm font-medium rounded-full">
              Customer Support Bot
            </span>
          </div>
          <h1 className="text-4xl font-bold mb-4 tracking-tight">
            Support Automation Assistant
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            A simulated environment for testing customer support automation. The bot 
            acts on behalf of a customer to interact with a simulated support agent.
          </p>
        </header>

        <ChatInterface />

        <Card className="max-w-2xl mx-auto mt-10 p-6 glass-light">
          <h2 className="text-xl font-semibold mb-3">Conversation Flow</h2>
          <ol className="list-decimal list-inside space-y-2 text-muted-foreground">
            <li>Bot introduces itself and asks for agent's name</li>
            <li>Bot confirms if it's in the right queue for coverage inquiries</li>
            <li>Bot provides member ID for authentication</li>
            <li>Bot inquires about plan status</li>
            <li>Conversation concludes</li>
          </ol>
          <p className="mt-4 text-sm text-muted-foreground">
            Note: This is a simulation. In a real implementation, this would connect 
            to LangChain and Groq LLM through a backend service.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Index;
