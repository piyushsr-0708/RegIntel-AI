import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    console.log('[LOGIN] Form submitted - username:', username);
    const result = await login(username, password);
    console.log('[LOGIN] Login result:', result);

    if (result.success) {
      console.log('[LOGIN] Login successful, user role:', result.user.role);
      // Redirect based on role
      if (result.user.role === 'head_office') {
        console.log('[LOGIN] Redirecting to / (Head Office dashboard)');
        navigate('/');
      } else {
        console.log('[LOGIN] Redirecting to /departments (Department dashboard)');
        navigate('/departments');
      }
    } else {
      console.log('[LOGIN] Login failed:', result.error);
      setError(result.error);
    }

    setLoading(false);
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
        fontFamily: "'Inter','Segoe UI',system-ui,sans-serif",
      }}
    >
      <div
        style={{
          background: '#1e293b',
          padding: '48px',
          borderRadius: '16px',
          boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
          width: '100%',
          maxWidth: '440px',
          border: '1px solid #334155',
        }}
      >
        {/* Logo/Branding */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div
            style={{
              fontSize: '32px',
              fontWeight: '700',
              background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '8px',
            }}
          >
            RegIntel AI
          </div>
          <div style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>
            Regulatory Intelligence Platform
          </div>
        </div>

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '600',
                color: '#e2e8f0',
                marginBottom: '8px',
              }}
            >
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              disabled={loading}
              placeholder="Enter your username"
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '14px',
                border: '1px solid #334155',
                borderRadius: '8px',
                background: '#0f172a',
                color: '#e2e8f0',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#10b981')}
              onBlur={(e) => (e.target.style.borderColor = '#334155')}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label
              style={{
                display: 'block',
                fontSize: '13px',
                fontWeight: '600',
                color: '#e2e8f0',
                marginBottom: '8px',
              }}
            >
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
              placeholder="Enter your password"
              style={{
                width: '100%',
                padding: '12px 16px',
                fontSize: '14px',
                border: '1px solid #334155',
                borderRadius: '8px',
                background: '#0f172a',
                color: '#e2e8f0',
                outline: 'none',
                transition: 'border-color 0.2s',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => (e.target.style.borderColor = '#10b981')}
              onBlur={(e) => (e.target.style.borderColor = '#334155')}
            />
          </div>

          {error && (
            <div
              style={{
                padding: '12px 16px',
                marginBottom: '24px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                color: '#fca5a5',
                fontSize: '13px',
                fontWeight: '500',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              fontSize: '14px',
              fontWeight: '600',
              color: '#fff',
              background: loading ? '#6b7280' : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              boxShadow: loading ? 'none' : '0 4px 12px rgba(16, 185, 129, 0.3)',
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 6px 16px rgba(16, 185, 129, 0.4)';
              }
            }}
            onMouseLeave={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.3)';
              }
            }}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Help Text */}
        <div
          style={{
            marginTop: '32px',
            padding: '16px',
            background: '#0f172a',
            borderRadius: '8px',
            border: '1px solid #334155',
          }}
        >
          <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '8px', fontWeight: '600' }}>
            Demo Credentials
          </div>
          <div style={{ fontSize: '11px', color: '#64748b', lineHeight: '1.6' }}>
            <strong style={{ color: '#e2e8f0' }}>Admin:</strong> admin / admin123<br />
            <strong style={{ color: '#e2e8f0' }}>Department:</strong> compliance / compliance123
          </div>
        </div>
      </div>
    </div>
  );
}
