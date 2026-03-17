import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { Rocket, AlertTriangle } from 'lucide-react';

const Login: React.FC = () => {
  const { loginWithRedirect, error } = useAuth0();

  const signup = () =>
    loginWithRedirect({ authorizationParams: { screen_hint: 'signup' } });

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="glass-panel max-w-md w-full p-8 text-center">
        <Rocket className="w-16 h-16 text-neonPurple mx-auto mb-6 animate-bounce" />
        <h1 className="text-4xl font-extrabold mb-2 bg-gradient-to-r from-neonPurple to-electricBlue bg-clip-text text-transparent">
          AuraOps
        </h1>
        <p className="text-gray-300 mb-8 font-light">High-Stakes Operator Command Center</p>
        
        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg flex items-center text-red-400 text-left">
            <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0" />
            <p className="text-sm">Auth Error: {error.message}</p>
          </div>
        )}
        
        <div className="space-y-4">
          <button
            onClick={() => loginWithRedirect()}
            className="w-full bg-neonPurple hover:bg-neonPurple/80 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-[0_0_20px_rgba(176,38,255,0.4)]"
          >
            Initialize Uplink (Login)
          </button>
          <button
            onClick={signup}
            className="w-full bg-transparent border border-electricBlue text-electricBlue hover:bg-electricBlue/10 font-bold py-3 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-[0_0_15px_rgba(15,240,252,0.2)]"
          >
            Register Operative (Signup)
          </button>
        </div>
      </div>
    </div>
  );
};

export default Login;
