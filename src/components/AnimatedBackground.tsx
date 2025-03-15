
import React from 'react';

const AnimatedBackground: React.FC = () => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-blue-50 opacity-80" />
      
      <div className="absolute top-0 left-0 w-full h-full">
        <div className="absolute top-[10%] right-[15%] w-[30rem] h-[30rem] bg-blue-100/20 rounded-full filter blur-3xl animate-breathing opacity-40" />
        <div className="absolute bottom-[20%] left-[10%] w-[20rem] h-[20rem] bg-blue-200/20 rounded-full filter blur-3xl animate-breathing opacity-30" 
          style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-[30%] right-[20%] w-[15rem] h-[15rem] bg-purple-100/10 rounded-full filter blur-3xl animate-breathing opacity-20" 
          style={{ animationDelay: '4s' }} />
      </div>
    </div>
  );
};

export default AnimatedBackground;
