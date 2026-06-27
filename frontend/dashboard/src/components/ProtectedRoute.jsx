import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  console.log('[PROTECTED_ROUTE] Checking access - isAuthenticated:', isAuthenticated, 'loading:', loading);

  if (loading) {
    console.log('[PROTECTED_ROUTE] Still loading, showing loading screen');
    return (
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          background: '#111827',
          color: '#10b981',
          fontSize: '14px',
          fontWeight: '600',
        }}
      >
        Verifying authentication...
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('[PROTECTED_ROUTE] Not authenticated, redirecting to /login');
    return <Navigate to="/login" replace />;
  }

  console.log('[PROTECTED_ROUTE] Authenticated, allowing access');
  return children;
}
