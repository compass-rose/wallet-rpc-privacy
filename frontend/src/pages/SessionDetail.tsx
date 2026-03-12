import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getSessionDetail } from "../api/sessions";

type SessionDetailData = {
  id: string;
  wallet_type: string;
  rpc_provider: string;
  status: string;
  packet_count?: number;
  created_at: string;
  updated_at?: string;
};

export default function SessionDetail() {
  const { id } = useParams();
  const [session, setSession] = useState<SessionDetailData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSession = async () => {
      try {
        if (!id) return;
        const res = await getSessionDetail(id);
        setSession(res.data);
      } catch (error) {
        console.error("Failed to fetch session detail:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
  }, [id]);

  if (loading) {
    return <div style={pageStyle}>Loading session detail...</div>;
  }

  if (!session) {
    return <div style={pageStyle}>Session not found</div>;
  }

  return (
    <div style={pageStyle}>
      <h1 style={titleStyle}>Session Detail</h1>

      <div style={cardStyle}>
        <div style={rowStyle}>
          <span style={labelStyle}>ID</span>
          <span style={valueStyle}>{session.id}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>Wallet Type</span>
          <span style={valueStyle}>{session.wallet_type}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>RPC Provider</span>
          <span style={valueStyle}>{session.rpc_provider}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>Status</span>
          <span style={valueStyle}>{session.status}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>Packet Count</span>
          <span style={valueStyle}>{session.packet_count ?? 0}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>Created At</span>
          <span style={valueStyle}>{session.created_at}</span>
        </div>

        <div style={rowStyle}>
          <span style={labelStyle}>Updated At</span>
          <span style={valueStyle}>{session.updated_at ?? "-"}</span>
        </div>
      </div>

      <div style={buttonGroupStyle}>
        <button style={buttonStyle}>View Traffic</button>
        <button style={buttonStyle}>View Leaks</button>
        <button style={buttonStyle}>Run Assessment</button>
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
  fontSize: "42px",
  fontWeight: 700,
  marginBottom: "24px",
};

const cardStyle: React.CSSProperties = {
  background: "#1f2937",
  border: "1px solid #374151",
  borderRadius: "16px",
  padding: "24px",
  boxShadow: "0 4px 14px rgba(0,0,0,0.18)",
  marginBottom: "24px",
};

const rowStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  gap: "16px",
  padding: "14px 0",
  borderBottom: "1px solid #374151",
};

const labelStyle: React.CSSProperties = {
  color: "#9ca3af",
  fontWeight: 600,
  minWidth: "140px",
};

const valueStyle: React.CSSProperties = {
  color: "#f9fafb",
  textAlign: "right",
  wordBreak: "break-all",
};

const buttonGroupStyle: React.CSSProperties = {
  display: "flex",
  gap: "12px",
  flexWrap: "wrap",
};

const buttonStyle: React.CSSProperties = {
  background: "#2563eb",
  color: "#fff",
  border: "none",
  borderRadius: "10px",
  padding: "12px 18px",
  cursor: "pointer",
  fontWeight: 600,
};