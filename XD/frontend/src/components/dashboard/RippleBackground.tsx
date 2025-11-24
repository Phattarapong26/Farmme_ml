import React from 'react';

interface RippleBackgroundProps {
  color?: string;
  opacity?: number;
}

const RippleBackground: React.FC<RippleBackgroundProps> = ({ 
  color = '#10b981', 
  opacity = 0.05 
}) => {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-50/30 via-white to-blue-50/30" />
      
      {/* Animated ripples */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full animate-ripple-1"
           style={{ 
             background: `radial-gradient(circle, ${color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
             animation: 'ripple 8s ease-in-out infinite'
           }} />
      
      <div className="absolute top-1/2 right-1/4 w-80 h-80 rounded-full animate-ripple-2"
           style={{ 
             background: `radial-gradient(circle, ${color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
             animation: 'ripple 10s ease-in-out infinite 2s'
           }} />
      
      <div className="absolute bottom-1/4 left-1/2 w-72 h-72 rounded-full animate-ripple-3"
           style={{ 
             background: `radial-gradient(circle, ${color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')} 0%, transparent 70%)`,
             animation: 'ripple 12s ease-in-out infinite 4s'
           }} />
      
      <style>{`
        @keyframes ripple {
          0%, 100% {
            transform: scale(1) translate(0, 0);
            opacity: 0.3;
          }
          50% {
            transform: scale(1.2) translate(20px, -20px);
            opacity: 0.6;
          }
        }
      `}</style>
    </div>
  );
};

export default RippleBackground;
