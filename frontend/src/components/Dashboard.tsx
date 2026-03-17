import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { CheckCircle, ShieldAlert, XCircle, LogOut } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

const Dashboard: React.FC = () => {
  const { user, logout, getAccessTokenSilently } = useAuth0();
  const [searchParams] = useSearchParams();
  
  // Read intent from URL param OR from sessionStorage (set before Auth0 redirect)
  const urlIntent = searchParams.get('intent');
  const storedIntent = sessionStorage.getItem('pending_intent');
  const intent = urlIntent || storedIntent;

  // Slack context - passed through the URL from the bot
  const channel = searchParams.get('channel') || sessionStorage.getItem('pending_channel') || undefined;
  const thread_ts = searchParams.get('thread_ts') || sessionStorage.getItem('pending_thread_ts') || undefined;
  const quantity = parseInt(searchParams.get('quantity') || sessionStorage.getItem('pending_quantity') || '50', 10);
  const amount = parseInt(searchParams.get('amount') || sessionStorage.getItem('pending_amount') || '10000', 10);

  const [status, setStatus] = useState<'idle' | 'authorizing' | 'success' | 'error'>('idle');

  // Clear the sessionStorage on mount once we've read it
  useEffect(() => {
    if (storedIntent) sessionStorage.removeItem('pending_intent');
    if (searchParams.get('channel')) {
      sessionStorage.setItem('pending_channel', searchParams.get('channel')!);
      sessionStorage.setItem('pending_thread_ts', searchParams.get('thread_ts') || '');
      sessionStorage.setItem('pending_quantity', searchParams.get('quantity') || '50');
      sessionStorage.setItem('pending_amount', searchParams.get('amount') || '10000');
    } else {
      // Clear session params after read
      sessionStorage.removeItem('pending_channel');
      sessionStorage.removeItem('pending_thread_ts');
      sessionStorage.removeItem('pending_quantity');
      sessionStorage.removeItem('pending_amount');
    }
  }, []);

  const handleLogout = () =>
    logout({ logoutParams: { returnTo: window.location.origin } });

  const handleAuthorize = async () => {
    setStatus('authorizing');
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          scope: intent === 'provision_wallets' ? 'write:wallets' : 'transfer:funds'
        }
      });
      
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/auth/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, intent, channel, thread_ts, quantity, amount })
      });
      
      if (response.ok) {
        setStatus('success');
      } else {
        setStatus('error');
      }
    } catch (e) {
      console.error(e);
      setStatus('error');
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <div className="absolute top-4 right-4 z-50">
        <button
          onClick={handleLogout}
          className="flex items-center text-gray-300 hover:text-white transition-colors"
        >
          <LogOut className="w-4 h-4 mr-2" /> Logout
        </button>
      </div>

      <div className="glass-panel max-w-lg w-full p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-electricBlue shadow-[0_0_10px_rgba(15,240,252,0.8)]" />
        
        <div className="flex items-center justify-center mb-6">
          <ShieldAlert className="w-12 h-12 text-neonPurple animate-pulse" />
        </div>
        
        <h2 className="text-2xl font-bold text-center mb-4">Authorization Required</h2>
        
        {user && (
          <div className="bg-white/5 rounded-lg p-4 mb-4 border border-white/10 text-left relative group">
            <p className="text-xs font-bold tracking-widest text-neonPurple mb-2 uppercase border-b border-white/10 pb-2">
              Operative Profile
            </p>
            <div className="max-h-40 overflow-y-auto scrollbar-thin scrollbar-thumb-neonPurple/50 scrollbar-track-transparent pr-2">
              <pre className="text-xs text-electricBlue font-mono whitespace-pre-wrap break-all">
                {JSON.stringify(user, null, 2)}
              </pre>
            </div>
          </div>
        )}
        
        <div className="bg-white/5 rounded-lg p-4 mb-8 border border-white/10">
          <p className="text-gray-300 text-sm mb-1">Agent Request:</p>
          <p className="font-mono text-electricBlue font-bold text-lg">
            {intent === 'provision_wallets' ? 'PROVISION_WALLETS' : 
             intent === 'pay_vendor' ? 'PAY_VENDOR' : 'UNKNOWN_OPERATION'}
          </p>
          <p className="text-sm mt-3 text-gray-400">
            Requested by: <span className="text-white">{user?.email}</span>
          </p>
        </div>

        {status === 'idle' && (
          <div className="space-y-4">
            <button
              onClick={handleAuthorize}
              disabled={!intent}
              className="w-full bg-neonPurple hover:bg-neonPurple/80 disabled:opacity-50 text-white font-bold py-3 px-6 rounded-lg transition-all duration-300 transform shadow-[0_0_20px_rgba(176,38,255,0.4)]"
            >
              AUTHORIZE AGENT
            </button>
            <button
              onClick={() => setStatus('error')}
              className="w-full bg-transparent border border-gray-600 hover:border-red-500 hover:text-red-500 text-gray-300 font-bold py-3 px-6 rounded-lg transition-colors"
            >
              DENY
            </button>
          </div>
        )}

        {status === 'authorizing' && (
          <div className="text-center py-4">
            <div className="inline-block w-8 h-8 border-4 border-neonPurple border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-electricBlue animate-pulse">Establishing Secure Uplink...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="text-center py-4">
            <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-green-400 mb-2">Authorization Granted</h3>
            <p className="text-gray-300 text-sm">You may close this window and return to Slack.</p>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center py-4">
            <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-red-500 mb-2">Authorization Failed or Denied</h3>
            <p className="text-gray-300 text-sm">Please retry the command in Slack.</p>
            <button onClick={() => setStatus('idle')} className="mt-4 text-sm text-electricBlue hover:underline">
              Reset Try
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
