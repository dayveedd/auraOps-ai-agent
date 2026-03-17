import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';

// Saves intent to sessionStorage before redirecting unauthenticated users
function AuthorizeRoute({ isAuthenticated }: { isAuthenticated: boolean }) {
  const location = useLocation();

  useEffect(() => {
    if (!isAuthenticated) {
      const params = new URLSearchParams(location.search);
      const intent = params.get('intent');
      if (intent) {
        sessionStorage.setItem('pending_intent', intent);
        if (params.get('channel')) sessionStorage.setItem('pending_channel', params.get('channel')!);
        if (params.get('thread_ts')) sessionStorage.setItem('pending_thread_ts', params.get('thread_ts')!);
        if (params.get('quantity')) sessionStorage.setItem('pending_quantity', params.get('quantity')!);
        if (params.get('amount')) sessionStorage.setItem('pending_amount', params.get('amount')!);
      }
    }
  }, [isAuthenticated, location]);

  return isAuthenticated ? <Dashboard /> : <Navigate to="/" replace />;
}

function App() {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center text-electricBlue text-2xl font-bold animate-pulse">
        Initializing Command Center...
      </div>
    );
  }

  return (
    <Router>
      <div className="relative z-10 w-full min-h-screen">
        <Routes>
          <Route path="/" element={!isAuthenticated ? <Login /> : <Navigate to="/authorize" replace />} />
          <Route path="/authorize" element={<AuthorizeRoute isAuthenticated={isAuthenticated} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
