import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getSessions, createSession, deleteSession } from "../api/sessions";
import { formatTime } from "../utils/time";

type SessionItem = {
  id: string;
  wallet_type: string;
  rpc_provider: string;
  status: string;
  packet_count?: number;
  created_at: string;
};

export default function Sessions() {
  const [sessions, setSessions] = useState<SessionItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [walletType, setWalletType] = useState("metamask");
  const [rpcProvider, setRpcProvider] = useState("infura");

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const res = await getSessions();
      setSessions(res.data.sessions || []);
    } catch (error) {
      console.error("Failed to fetch sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleCreate = async () => {
    try {
      await createSession({
        wallet_type: walletType,
        rpc_provider: rpcProvider,
      });
      fetchSessions();
    } catch (error) {
      console.error("Failed to create session:", error);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteSession(id);
      fetchSessions();
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  if (loading) {
    return <div style={pageStyle}>Loading sessions...</div>;
  }

  return (
    <div style={pageStyle}>
      <h1 style={titleStyle}>Sessions</h1>

      <div style={createBoxStyle}>
        <h2 style={sectionTitleStyle}>Create New Session</h2>

        <div style={formRowStyle}>
          <div style={inputGroupStyle}>
            <label style={labelStyle}>Wallet Type</label>
            <input
              style={inputStyle}
              value={walletType}
              onChange={(e) => setWalletType(e.target.value)}
            />
          </div>

          <div style={inputGroupStyle}>
            <label style={labelStyle}>RPC Provider</label>
            <input
              style={inputStyle}
              value={rpcProvider}
              onChange={(e) => setRpcProvider(e.target.value)}
            />
          </div>

          <button style={buttonStyle} onClick={handleCreate}>
            Create Session
          </button>
        </div>
      </div>

      <div style={tableBoxStyle}>
        <h2 style={sectionTitleStyle}>Session List</h2>

        {sessions.length === 0 ? (
          <div style={emptyStyle}>No sessions found</div>
        ) : (
          <table style={tableStyle}>
            <thead>
              <tr>
                <th style={thStyle}>ID</th>
                <th style={thStyle}>Wallet Type</th>
                <th style={thStyle}>RPC Provider</th>
                <th style={thStyle}>Status</th>
                <th style={thStyle}>Packet Count</th>
                <th style={thStyle}>Created At</th>
                <th style={thStyle}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((session) => (
                <tr key={session.id}>
                  <td style={tdStyle}>
                    <Link
                      to={`/sessions/${session.id}`}
                      style={{
                        color: "#60a5fa",
                        textDecoration: "none",
                        fontWeight: 600,
                      }}
                    >
                      {session.id}
                    </Link>
                  </td>
                  <td style={tdStyle}>{session.wallet_type}</td>
                  <td style={tdStyle}>{session.rpc_provider}</td>
                  <td style={tdStyle}>{session.status}</td>
                  <td style={tdStyle}>{session.packet_count ?? 0}</td>
                  <td>
                <div style={{ lineHeight: "1.3" }}>
                    <div>{formatTime(session.created_at).date}</div>
                    <div style={{ color: "#9ca3af", fontSize: "13px" }}>
                    {formatTime(session.created_at).time}
                    </div>
                </div>
                </td>
                  <td style={tdStyle}>
                    <button
                      style={deleteButtonStyle}
                      onClick={() => handleDelete(session.id)}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const pageStyle: React.CSSProperties = {
  padding: "32px",
  color: "#f9fafb",
  minHeight: "100vh",
  background: "#111827",
  fontFamily:
    "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
};

const titleStyle: React.CSSProperties = {
  fontSize: "48px",
  fontWeight: 700,
  marginBottom: "24px",
};

const sectionTitleStyle: React.CSSProperties = {
  fontSize: "28px",
  fontWeight: 700,
  marginBottom: "16px",
};

const createBoxStyle: React.CSSProperties = {
  background: "#1f2937",
  border: "1px solid #374151",
  borderRadius: "16px",
  padding: "24px",
  marginBottom: "24px",
};

const formRowStyle: React.CSSProperties = {
  display: "flex",
  gap: "16px",
  alignItems: "end",
  flexWrap: "wrap",
};

const inputGroupStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const labelStyle: React.CSSProperties = {
  fontSize: "14px",
  color: "#d1d5db",
};

const inputStyle: React.CSSProperties = {
  background: "#111827",
  border: "1px solid #4b5563",
  color: "#f9fafb",
  padding: "10px 12px",
  borderRadius: "8px",
  minWidth: "220px",
};

const buttonStyle: React.CSSProperties = {
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  padding: "11px 18px",
  cursor: "pointer",
  fontWeight: 600,
};

const deleteButtonStyle: React.CSSProperties = {
  background: "#dc2626",
  color: "#fff",
  border: "none",
  borderRadius: "8px",
  padding: "8px 12px",
  cursor: "pointer",
};

const tableBoxStyle: React.CSSProperties = {
  background: "#1f2937",
  border: "1px solid #374151",
  borderRadius: "16px",
  padding: "24px",
};

const tableStyle: React.CSSProperties = {
  width: "100%",
  borderCollapse: "collapse",
};

const thStyle: React.CSSProperties = {
  textAlign: "left",
  padding: "12px",
  borderBottom: "1px solid #374151",
  color: "#d1d5db",
  fontSize: "14px",
};

const tdStyle: React.CSSProperties = {
  padding: "12px",
  borderBottom: "1px solid #374151",
  fontSize: "14px",
  verticalAlign: "top",
  wordBreak: "break-all",
};

const emptyStyle: React.CSSProperties = {
  color: "#9ca3af",
  padding: "16px 0",
};