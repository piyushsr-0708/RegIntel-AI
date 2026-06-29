import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import FullTextModal from '../components/FullTextModal';

export default function DepartmentWorkspace() {
  const { api, user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [completing, setCompleting] = useState({});
  const [selectedTask, setSelectedTask] = useState(null);
  const [showFullText, setShowFullText] = useState(false);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const response = await api.get('/departments/workspace/my-tasks');
      setTasks(response.data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViewFullText = (task) => {
    setSelectedTask(task);
    setShowFullText(true);
  };

  const closeFullText = () => {
    setShowFullText(false);
    setSelectedTask(null);
  };

  const handleMarkCompleted = async (assignmentId) => {
    setCompleting({ ...completing, [assignmentId]: true });
    
    try {
      await api.post(`/departments/workspace/tasks/${assignmentId}/complete`);
      alert('Task marked as completed!');
      
      // Reload tasks
      await loadTasks();
    } catch (error) {
      console.error('Failed to mark completed:', error);
      alert('Failed to update task status');
    } finally {
      setCompleting({ ...completing, [assignmentId]: false });
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#10b981';
      default: return '#64748b';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: 40, color: '#94a3b8' }}>
        Loading your tasks...
      </div>
    );
  }

  const completedCount = tasks.filter(t => t.status === 'completed').length;
  const pendingCount = tasks.length - completedCount;

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 700, color: '#f8fafc', marginBottom: 8 }}>
          My Assignments
        </h1>
        <p style={{ fontSize: 14, color: '#94a3b8' }}>
          {user?.department?.name || 'Department'} Dashboard
        </p>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, marginBottom: 32 }}>
        <div style={{
          background: 'linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%)',
          borderRadius: 12,
          padding: 20,
          border: '1px solid rgba(59,130,246,0.3)'
        }}>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', marginBottom: 4 }}>
            Total Tasks
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
            {tasks.length}
          </div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #047857 0%, #059669 100%)',
          borderRadius: 12,
          padding: 20,
          border: '1px solid rgba(16,185,129,0.3)'
        }}>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', marginBottom: 4 }}>
            Completed
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
            {completedCount}
          </div>
        </div>

        <div style={{
          background: 'linear-gradient(135deg, #b45309 0%, #d97706 100%)',
          borderRadius: 12,
          padding: 20,
          border: '1px solid rgba(245,158,11,0.3)'
        }}>
          <div style={{ fontSize: 14, color: 'rgba(255,255,255,0.7)', marginBottom: 4 }}>
            Remaining
          </div>
          <div style={{ fontSize: 32, fontWeight: 700, color: '#fff' }}>
            {pendingCount}
          </div>
        </div>
      </div>

      {/* No Tasks Message */}
      {tasks.length === 0 && (
        <div style={{ textAlign: 'center', padding: 60 }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>📝</div>
          <div style={{ fontSize: 18, fontWeight: 600, color: '#cbd5e1', marginBottom: 8 }}>
            No Tasks Assigned Yet
          </div>
          <div style={{ fontSize: 14, color: '#64748b' }}>
            Your tasks will appear here once they are published by Head Office
          </div>
        </div>
      )}

      {/* Task Cards */}
      <div style={{ display: 'grid', gap: 16 }}>
        {tasks.map((task) => (
          <div
            key={task.assignment_id}
            style={{
              background: task.status === 'completed' 
                ? 'rgba(16,185,129,0.05)' 
                : '#1e293b',
              borderRadius: 12,
              padding: 24,
              border: task.status === 'completed' 
                ? '1px solid rgba(16,185,129,0.3)' 
                : '1px solid rgba(148,163,184,0.1)',
              opacity: task.status === 'completed' ? 0.7 : 1,
              transition: 'all 0.2s'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
              {/* Priority Badge */}
              <div style={{
                display: 'inline-block',
                background: `${getPriorityColor(task.priority)}20`,
                color: getPriorityColor(task.priority),
                padding: '4px 12px',
                borderRadius: 6,
                fontSize: 11,
                fontWeight: 700,
                letterSpacing: 0.5,
                textTransform: 'uppercase'
              }}>
                {task.priority || 'Medium'}
              </div>

              {/* Status Badge */}
              <div style={{
                background: task.status === 'completed' 
                  ? 'rgba(16,185,129,0.15)' 
                  : 'rgba(59,130,246,0.15)',
                color: task.status === 'completed' ? '#10b981' : '#3b82f6',
                padding: '6px 12px',
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 600
              }}>
                {task.status === 'completed' ? '✓ Completed' : 'Assigned'}
              </div>
            </div>

            {/* Domain */}
            {task.domain && (
              <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8, fontWeight: 600 }}>
                {task.domain.toUpperCase()}
              </div>
            )}

            {/* Requirement Text */}
            <div 
              onClick={() => handleViewFullText(task)}
              style={{ 
                fontSize: 15, 
                color: '#e2e8f0', 
                lineHeight: 1.6, 
                marginBottom: 16,
                cursor: 'pointer',
                padding: 12,
                background: 'rgba(255,255,255,0.02)',
                borderRadius: 8,
                border: '1px solid transparent',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(96,165,250,0.08)';
                e.currentTarget.style.borderColor = 'rgba(96,165,250,0.2)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255,255,255,0.02)';
                e.currentTarget.style.borderColor = 'transparent';
              }}
            >
              {task.requirement_text && task.requirement_text.length > 200
                ? `${task.requirement_text.substring(0, 200)}...`
                : task.requirement_text || 'No description available'}
              {task.requirement_text && task.requirement_text.length > 200 && (
                <div style={{ marginTop: 8, fontSize: 12, color: '#60a5fa', fontWeight: 600 }}>
                  Click to view full text →
                </div>
              )}
            </div>

            {/* Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: 16, borderTop: '1px solid rgba(148,163,184,0.1)' }}>
              <div style={{ fontSize: 12, color: '#64748b' }}>
                Assigned: {new Date(task.assigned_at).toLocaleDateString()}
              </div>

              {/* Mark Completed Button */}
              {task.status !== 'completed' && (
                <button
                  onClick={() => handleMarkCompleted(task.assignment_id)}
                  disabled={completing[task.assignment_id]}
                  style={{
                    background: completing[task.assignment_id]
                      ? '#64748b'
                      : 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    color: '#fff',
                    border: 'none',
                    borderRadius: 8,
                    padding: '10px 24px',
                    fontSize: 13,
                    fontWeight: 600,
                    cursor: completing[task.assignment_id] ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s',
                    boxShadow: completing[task.assignment_id]
                      ? 'none'
                      : '0 4px 12px rgba(16,185,129,0.3)'
                  }}
                  onMouseEnter={(e) => {
                    if (!completing[task.assignment_id]) {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 6px 16px rgba(16,185,129,0.4)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = completing[task.assignment_id]
                      ? 'none'
                      : '0 4px 12px rgba(16,185,129,0.3)';
                  }}
                >
                  {completing[task.assignment_id] ? 'Updating...' : 'Mark Completed'}
                </button>
              )}

              {task.status === 'completed' && task.completed_at && (
                <div style={{ fontSize: 12, color: '#10b981', fontWeight: 600 }}>
                  ✓ Completed on {new Date(task.completed_at).toLocaleDateString()}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Full Text Modal */}
      <FullTextModal
        isOpen={showFullText}
        onClose={closeFullText}
        data={selectedTask ? {
          requirement: {
            requirement_id: selectedTask.requirement_id || 'N/A',
            text: selectedTask.requirement_text,
            priority: selectedTask.priority,
            domain: selectedTask.domain,
          },
          department_name: user?.department?.name,
          status: selectedTask.status,
          assigned_at: selectedTask.assigned_at,
          completed_at: selectedTask.completed_at,
        } : null}
        type="assignment"
      />
    </div>
  );
}
