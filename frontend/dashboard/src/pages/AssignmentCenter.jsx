import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useAnalysisSession } from '../context/AnalysisSession';
import FullTextModal from '../components/FullTextModal';

export default function AssignmentCenter() {
  const { api } = useAuth();
  const { hasSession, resetSession } = useAnalysisSession();
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState({});
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [showFullText, setShowFullText] = useState(false);
  const [loadingFullText, setLoadingFullText] = useState(false);

  useEffect(() => {
    console.log('[ASSIGNMENT_CENTER] Loading summary from backend (session state:', hasSession, ')');
    loadSummary();
  }, [hasSession]); // Reload when session state changes

  const loadSummary = async () => {
    setLoading(true);
    try {
      const response = await api.get('/assignment-center/summary');
      console.log('[ASSIGNMENT_CENTER] Summary loaded:', response.data);
      setSummary(response.data);
    } catch (error) {
      console.error('Failed to load assignment summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewFullText = async (assignmentId) => {
    setLoadingFullText(true);
    try {
      const response = await api.get(`/admin/assignments/${assignmentId}`);
      setSelectedAssignment(response.data);
      setShowFullText(true);
    } catch (error) {
      console.error('Failed to load assignment details:', error);
      alert('Failed to load full text');
    } finally {
      setLoadingFullText(false);
    }
  };

  const closeFullText = () => {
    setShowFullText(false);
    setSelectedAssignment(null);
  };

  const handlePublish = async (departmentId) => {
    setPublishing({ ...publishing, [departmentId]: true });
    
    try {
      await api.post('/assignment-center/publish', {
        department_id: departmentId
      });
      
      alert('Assignments published successfully!');
      
      // Reload summary
      await loadSummary();
    } catch (error) {
      console.error('Failed to publish:', error);
      alert('Failed to publish assignments');
    } finally {
      setPublishing({ ...publishing, [departmentId]: false });
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>
        Loading assignments...
      </div>
    );
  }

  if (!summary || !summary.departments || summary.departments.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: 60 }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>📋</div>
        <div style={{ fontSize: 18, fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
          No Assignments to Review
        </div>
        <div style={{ fontSize: 14, color: '#64748b' }}>
          Run the pipeline to generate department assignments
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: '#f8fafc', marginBottom: 8 }}>
          Assignment Center
        </h1>
        <p style={{ fontSize: 14, color: '#94a3b8' }}>
          Review and publish department assignments
        </p>
      </div>

      {/* Summary Card */}
      <div style={{
        background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
        borderRadius: 12,
        padding: 24,
        marginBottom: 24,
        border: '1px solid rgba(59,130,246,0.3)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 48,
            height: 48,
            borderRadius: 10,
            background: 'rgba(255,255,255,0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24
          }}>
            📊
          </div>
          <div>
            <div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
              {summary.total_maps}
            </div>
            <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)' }}>
              Pending MAPs (Assignments) Across {summary.departments.length} Departments
            </div>
          </div>
        </div>
      </div>

      {/* Department Cards */}
      <div style={{ display: 'grid', gap: 16 }}>
        {summary.departments.map((dept) => (
          <div
            key={dept.department_id}
            style={{
              background: '#1e293b',
              borderRadius: 12,
              padding: 24,
              border: '1px solid rgba(148,163,184,0.1)',
              transition: 'all 0.2s'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              {/* Department Info */}
              <div style={{ flex: 1 }}>
                <h3 style={{ fontSize: 20, fontWeight: 600, color: '#f8fafc', marginBottom: 8 }}>
                  {dept.department_name}
                </h3>
                <div style={{ display: 'flex', gap: 24, marginBottom: 4 }}>
                  <div>
                    <span style={{ fontSize: 28, fontWeight: 700, color: '#3b82f6' }}>
                      {dept.task_count}
                    </span>
                    <span style={{ fontSize: 14, color: '#94a3b8', marginLeft: 8 }}>
                      Tasks
                    </span>
                  </div>
                </div>
              </div>

              {/* Publish Button */}
              <button
                onClick={() => handlePublish(dept.department_id)}
                disabled={publishing[dept.department_id]}
                style={{
                  background: publishing[dept.department_id] 
                    ? '#64748b' 
                    : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: 8,
                  padding: '12px 28px',
                  fontSize: 14,
                  fontWeight: 600,
                  cursor: publishing[dept.department_id] ? 'not-allowed' : 'pointer',
                  transition: 'all 0.2s',
                  boxShadow: publishing[dept.department_id] 
                    ? 'none' 
                    : '0 4px 12px rgba(16,185,129,0.3)'
                }}
                onMouseEnter={(e) => {
                  if (!publishing[dept.department_id]) {
                    e.target.style.transform = 'translateY(-2px)';
                    e.target.style.boxShadow = '0 6px 16px rgba(16,185,129,0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.target.style.transform = 'translateY(0)';
                  e.target.style.boxShadow = publishing[dept.department_id] 
                    ? 'none' 
                    : '0 4px 12px rgba(16,185,129,0.3)';
                }}
              >
                {publishing[dept.department_id] ? 'Publishing...' : 'Publish'}
              </button>
            </div>

            {/* Requirements Preview (Optional - show first 3) */}
            {dept.requirements && dept.requirements.length > 0 && (
              <div style={{ marginTop: 16, paddingTop: 16, borderTop: '1px solid rgba(148,163,184,0.1)' }}>
                <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8, fontWeight: 600 }}>
                  SAMPLE REQUIREMENTS
                </div>
                {dept.requirements.slice(0, 3).map((req, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleViewFullText(req.assignment_id)}
                    style={{
                      fontSize: 13,
                      color: '#cbd5e1',
                      marginBottom: 6,
                      paddingLeft: 12,
                      borderLeft: '2px solid rgba(59,130,246,0.3)',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      padding: '8px 12px',
                      borderRadius: 6,
                      background: 'transparent'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'rgba(59,130,246,0.1)';
                      e.currentTarget.style.borderLeftColor = '#3b82f6';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.borderLeftColor = 'rgba(59,130,246,0.3)';
                    }}
                  >
                    {req.requirement_text.substring(0, 200)}...
                    <div style={{ fontSize: 11, color: '#60a5fa', marginTop: 4 }}>
                      Click to view full text →
                    </div>
                  </div>
                ))}
                {dept.requirements.length > 3 && (
                  <div style={{ fontSize: 12, color: '#64748b', marginTop: 8 }}>
                    +{dept.requirements.length - 3} more requirements
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Full Text Modal */}
      <FullTextModal
        isOpen={showFullText}
        onClose={closeFullText}
        data={selectedAssignment}
        type="assignment"
      />
    </div>
  );
}
