import { useState, useEffect } from 'react';
import { Calendar, CreditCard, Wallet, ExternalLink, RefreshCw } from 'lucide-react';

interface AgentAction {
  id: string;
  type: 'wallet' | 'payment' | 'calendar';
  title: string;
  status: string;
  created_at: string;
  link?: string;
  amounts?: string;
}

export default function ActionHistory() {
  const [actions, setActions] = useState<AgentAction[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchActions = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/agent-actions`);
      if (res.ok) {
        const data = await res.json();
        setActions(data);
      }
    } catch (e) {
      console.error("Failed to fetch agent actions", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
  }, []);

  const getIcon = (type: string) => {
    switch (type) {
      case 'wallet': return <Wallet className="w-5 h-5 text-neonPurple" />;
      case 'payment': return <CreditCard className="w-5 h-5 text-green-400" />;
      case 'calendar': return <Calendar className="w-5 h-5 text-electricBlue" />;
      default: return <Wallet className="w-5 h-5" />;
    }
  };

  return (
    <div className="glass-panel w-full p-6 mt-8 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-1 h-full bg-neonPurple shadow-[0_0_10px_rgba(176,38,255,0.8)]" />
      
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
          Agent Action Log
        </h3>
        <button 
          onClick={fetchActions}
          className="p-2 text-gray-400 hover:text-white hover:bg-white/5 rounded-full transition-colors"
          title="Refresh Logs"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-electricBlue' : ''}`} />
        </button>
      </div>

      {loading && actions.length === 0 ? (
        <div className="text-center py-8 text-gray-400 text-sm animate-pulse">
          Decrypting audit logs...
        </div>
      ) : actions.length === 0 ? (
        <div className="text-center py-8 text-gray-500 text-sm">
          No agent actions recorded yet.
        </div>
      ) : (
        <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          {actions.map((action) => (
            <div 
              key={action.id} 
              className="flex items-center p-4 bg-black/20 rounded-lg border border-white/5 hover:bg-black/30 transition-colors group"
            >
              <div className="p-3 bg-white/5 rounded-lg mr-4 group-hover:bg-white/10 transition-colors">
                {getIcon(action.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-sm font-semibold text-gray-200 truncate pr-4">{action.title}</h4>
                  <span className="text-xs text-gray-500 whitespace-nowrap">
                    {new Date(action.created_at).toLocaleString(undefined, {
                      month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                    })}
                  </span>
                </div>
                
                <div className="flex items-center text-xs text-gray-400">
                  <span className={`px-2 py-0.5 rounded-full border mr-3 ${
                    action.status === 'success' || action.status === 'created' || action.status === 'active' 
                      ? 'bg-green-500/10 border-green-500/30 text-green-400'
                      : action.status === 'initialized'
                      ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                      : 'bg-gray-500/10 border-gray-500/30 text-gray-400'
                  }`}>
                    {action.status.toUpperCase()}
                  </span>
                  
                  {action.amounts && (
                    <span className="text-electricBlue mr-3">{action.amounts}</span>
                  )}
                  
                  {action.link && (
                    <a 
                      href={action.link} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-neonPurple hover:text-white transition-colors ml-auto"
                    >
                      View Link <ExternalLink className="w-3 h-3 ml-1" />
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
