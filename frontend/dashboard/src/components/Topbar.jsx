import { useNavigate } from "react-router-dom";
import { useState, useEffect, useRef } from "react";
import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef(null);

  // Close menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
    };

    if (showUserMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showUserMenu]);

  const handleLogout = () => {
    console.log('[TOPBAR] Logout button clicked');
    logout();
    console.log('[TOPBAR] Navigating to /login');
    navigate('/login');
  };

  // Format role for display
  const formatRole = (role) => {
    if (role === 'head_office') return 'Head Office';
    return role.charAt(0).toUpperCase() + role.slice(1);
  };

  return (
    <header style={{
      position: "sticky", top: 0, zIndex: 100,
      background: "#0f1923",
      borderBottom: "1px solid rgba(16,185,129,0.15)",
      boxShadow: "0 2px 20px rgba(0,0,0,0.35)",
    }}>
      <div style={{ padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 60 }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg,#10b981,#059669)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 14px rgba(16,185,129,0.45)",
          }}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#fff" strokeWidth="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <div style={{ color: "#f8fafc", fontWeight: 800, fontSize: 14, letterSpacing: 0.2, lineHeight: 1 }}>RegIntel AI</div>
            <div style={{ color: "#10b981", fontSize: 9, fontWeight: 600, letterSpacing: 0.5, lineHeight: 1, marginTop: 2 }}>Compliance Platform</div>
          </div>
        </div>

        {/* Right section: Live badge + User info */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, flexShrink: 0 }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)",
            borderRadius: 20, padding: "5px 12px",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", display: "inline-block", animation: "pulse-dot 2s ease-in-out infinite" }} />
            <span style={{ color: "#10b981", fontSize: 11, fontWeight: 700, letterSpacing: 0.3 }}>LIVE</span>
          </div>

          {/* User Info & Logout */}
          {user && (
            <div ref={menuRef} style={{ position: 'relative' }}>
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  background: 'rgba(16,185,129,0.1)',
                  border: '1px solid rgba(16,185,129,0.2)',
                  borderRadius: 8,
                  padding: '6px 12px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(16,185,129,0.15)';
                  e.currentTarget.style.borderColor = 'rgba(16,185,129,0.3)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(16,185,129,0.1)';
                  e.currentTarget.style.borderColor = 'rgba(16,185,129,0.2)';
                }}
              >
                <div style={{
                  width: 28,
                  height: 28,
                  borderRadius: 6,
                  background: 'linear-gradient(135deg, #10b981, #059669)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: 12,
                  fontWeight: 700,
                }}>
                  {user.username.charAt(0).toUpperCase()}
                </div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: '#e2e8f0', lineHeight: 1 }}>
                    {user.username}
                  </div>
                  <div style={{ fontSize: 10, fontWeight: 600, color: '#10b981', lineHeight: 1, marginTop: 2 }}>
                    {formatRole(user.role)}
                  </div>
                </div>
                <svg
                  width="12"
                  height="12"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="#94a3b8"
                  strokeWidth="3"
                  style={{ transition: 'transform 0.2s', transform: showUserMenu ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Dropdown Menu */}
              {showUserMenu && (
                <div
                  style={{
                    position: 'absolute',
                    top: '100%',
                    right: 0,
                    marginTop: 8,
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: 8,
                    boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
                    minWidth: 200,
                    overflow: 'hidden',
                    zIndex: 1000,
                  }}
                >
                  <div style={{ padding: '12px 16px', borderBottom: '1px solid #334155' }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: '#e2e8f0', marginBottom: 4 }}>
                      {user.full_name || user.username}
                    </div>
                    <div style={{ fontSize: 11, color: '#94a3b8' }}>
                      {user.email || 'No email'}
                    </div>
                    <div style={{ fontSize: 10, fontWeight: 600, color: '#10b981', marginTop: 6 }}>
                      Role: {formatRole(user.role)}
                    </div>
                    {user.department && user.department.name && (
                      <div style={{ fontSize: 10, fontWeight: 600, color: '#06b6d4', marginTop: 2 }}>
                        Department: {user.department.name}
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleLogout}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      background: 'transparent',
                      border: 'none',
                      color: '#f87171',
                      fontSize: 13,
                      fontWeight: 600,
                      textAlign: 'left',
                      cursor: 'pointer',
                      transition: 'background 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(248, 113, 113, 0.1)')}
                    onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                  >
                    <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                    Logout
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
