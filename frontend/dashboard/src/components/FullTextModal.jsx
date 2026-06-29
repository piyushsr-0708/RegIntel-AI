import React from "react";

/**
 * Full Text Modal Component
 * Displays complete requirement or assignment text without truncation
 */
export default function FullTextModal({ isOpen, onClose, data, type = "requirement" }) {
  if (!isOpen || !data) return null;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      onClick={handleBackdropClick}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: "rgba(0, 0, 0, 0.75)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 9999,
        padding: 20,
      }}
    >
      <div
        style={{
          background: "#1a2332",
          borderRadius: 12,
          maxWidth: 900,
          width: "100%",
          maxHeight: "90vh",
          display: "flex",
          flexDirection: "column",
          border: "1px solid rgba(255,255,255,0.1)",
          boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "20px 24px",
            borderBottom: "1px solid rgba(255,255,255,0.1)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontSize: 18, fontWeight: 800, color: "#f1f5f9", marginBottom: 4 }}>
              {type === "assignment" ? "Assignment Details" : "Requirement Details"}
            </div>
            <div style={{ fontSize: 12, color: "#64748b", fontFamily: "monospace", fontWeight: 600 }}>
              {type === "assignment" && data.requirement?.requirement_id
                ? `Requirement: ${data.requirement.requirement_id}`
                : data.requirement_id || data.req_id || "ID not available"}
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "none",
              color: "#94a3b8",
              fontSize: 24,
              cursor: "pointer",
              padding: 0,
              width: 32,
              height: 32,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: 6,
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "rgba(255,255,255,0.1)";
              e.currentTarget.style.color = "#f1f5f9";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
              e.currentTarget.style.color = "#94a3b8";
            }}
          >
            ×
          </button>
        </div>

        {/* Metadata */}
        <div
          style={{
            padding: "16px 24px",
            borderBottom: "1px solid rgba(255,255,255,0.05)",
            background: "#162030",
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12 }}>
            {type === "assignment" && (
              <>
                {data.department_name && (
                  <div>
                    <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>DEPARTMENT</div>
                    <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 600 }}>{data.department_name}</div>
                  </div>
                )}
                {data.status && (
                  <div>
                    <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>STATUS</div>
                    <div
                      style={{
                        fontSize: 11,
                        color:
                          data.status === "completed"
                            ? "#34d399"
                            : data.status === "in_progress"
                            ? "#60a5fa"
                            : "#fbbf24",
                        fontWeight: 700,
                        textTransform: "uppercase",
                      }}
                    >
                      {data.status}
                    </div>
                  </div>
                )}
              </>
            )}
            {(data.priority || data.requirement?.priority) && (
              <div>
                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>PRIORITY</div>
                <div
                  style={{
                    fontSize: 11,
                    color:
                      (data.priority || data.requirement?.priority) === "Critical"
                        ? "#ef4444"
                        : (data.priority || data.requirement?.priority) === "High"
                        ? "#fbbf24"
                        : "#60a5fa",
                    fontWeight: 700,
                  }}
                >
                  {data.priority || data.requirement?.priority}
                </div>
              </div>
            )}
            {(data.classification || data.requirement?.classification) && (
              <div>
                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>CLASSIFICATION</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 600 }}>
                  {data.classification || data.requirement?.classification}
                </div>
              </div>
            )}
            {(data.domain || data.requirement?.domain) && (
              <div>
                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>DOMAIN</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 600 }}>{data.domain || data.requirement?.domain}</div>
              </div>
            )}
            {(data.source_reference || data.requirement?.source_reference || data.source_document) && (
              <div>
                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 2 }}>SOURCE</div>
                <div style={{ fontSize: 13, color: "#e2e8f0", fontWeight: 600 }}>
                  {data.source_reference || data.requirement?.source_reference || data.source_document}
                </div>
              </div>
            )}
            {data.departments && data.departments.length > 0 && (
              <div style={{ gridColumn: "1 / -1" }}>
                <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>ASSIGNED DEPARTMENTS</div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {data.departments.map((dept, idx) => (
                    <div
                      key={idx}
                      style={{
                        padding: "4px 10px",
                        borderRadius: 6,
                        background: "rgba(96,165,250,0.1)",
                        border: "1px solid rgba(96,165,250,0.2)",
                        fontSize: 11,
                        color: "#60a5fa",
                        fontWeight: 600
                      }}
                    >
                      {dept.name}
                      {dept.status && (
                        <span style={{ marginLeft: 6, color: "#64748b", fontSize: 10 }}>
                          ({dept.status})
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Full Text Content */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            padding: "24px",
          }}
        >
          <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 8 }}>FULL TEXT</div>
          <div
            style={{
              fontSize: 14,
              color: "#e2e8f0",
              lineHeight: 1.7,
              whiteSpace: "pre-wrap",
              wordWrap: "break-word",
            }}
          >
            {type === "assignment" ? data.requirement?.text || "No text available" : data.text || "No text available"}
          </div>

          {/* Additional metadata for assignments */}
          {type === "assignment" && data.remarks && (
            <div style={{ marginTop: 24, paddingTop: 24, borderTop: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 8 }}>REMARKS</div>
              <div
                style={{
                  fontSize: 13,
                  color: "#94a3b8",
                  lineHeight: 1.6,
                  whiteSpace: "pre-wrap",
                }}
              >
                {data.remarks}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div
          style={{
            padding: "16px 24px",
            borderTop: "1px solid rgba(255,255,255,0.1)",
            display: "flex",
            justifyContent: "flex-end",
          }}
        >
          <button
            onClick={onClose}
            style={{
              padding: "10px 24px",
              borderRadius: 8,
              background: "#60a5fa",
              color: "#fff",
              border: "none",
              fontSize: 13,
              fontWeight: 700,
              cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#3b82f6";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "#60a5fa";
            }}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
