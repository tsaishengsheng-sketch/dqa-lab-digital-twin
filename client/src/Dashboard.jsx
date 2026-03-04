import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
} from "recharts";

const API = "http://localhost:8000";

const STATUS_CONFIG = {
  OFFLINE: { color: "#484f58", bg: "#21262d" },
  IDLE: { color: "#8b949e", bg: "#21262d" },
  RUNNING: { color: "#3fb950", bg: "#0f2318" },
  PAUSED: { color: "#f0a500", bg: "#2d1f00" },
  FINISHING: { color: "#58a6ff", bg: "#0d1f33" },
  EMERGENCY: { color: "#f85149", bg: "#2d0f0f" },
};

const Dashboard = () => {
  const [data, setData] = useState({
    temperature: 0,
    humidity: 0,
    status: "OFFLINE",
    timestamp: "--:--:--",
    running_sop_name: "None",
    description: "等待連線...",
  });
  const [history, setHistory] = useState([]);
  const [executions, setExecutions] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`${API}/api/latest`);
        const json = res.data;
        if (json.temperature !== undefined) {
          setData(json);
          setHistory((prev) => [
            ...prev.slice(-59),
            { ...json, time: json.timestamp },
          ]);
        }
      } catch (err) {}
    };
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    axios
      .get(`${API}/api/reports/list`)
      .then((r) => setExecutions(r.data))
      .catch(() => {});
  }, []);

  const sc = STATUS_CONFIG[data.status] || STATUS_CONFIG.OFFLINE;
  const isActive = ["RUNNING", "FINISHING", "PAUSED", "EMERGENCY"].includes(
    data.status,
  );

  const card = {
    background: "#161b22",
    border: "1px solid #30363d",
    borderRadius: 12,
    padding: "20px 24px",
  };

  return (
    <div
      style={{
        backgroundColor: "#0d1117",
        color: "#cdd9e5",
        minHeight: "100vh",
        padding: "24px 28px",
        fontFamily: "system-ui, -apple-system, sans-serif",
        boxSizing: "border-box",
        width: "100%",
      }}
    >
      {/* ── 標題列 ── */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #30363d",
          paddingBottom: 16,
          marginBottom: 24,
        }}
      >
        <h1
          style={{ color: "#58a6ff", margin: 0, fontSize: 22, fontWeight: 700 }}
        >
          KSON AICM | Digital Twin
        </h1>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span
            style={{
              padding: "2px 10px",
              borderRadius: 4,
              fontSize: 12,
              fontWeight: 700,
              color: sc.color,
              background: sc.bg,
              border: `1px solid ${sc.color}44`,
            }}
          >
            {data.status}
          </span>
          <span style={{ fontSize: 11, color: "#484f58" }}>
            {data.timestamp}
          </span>
        </div>
      </div>

      {/* ── 當前任務 ── */}
      <div
        style={{
          ...card,
          borderLeft: `3px solid ${sc.color}`,
          marginBottom: 24,
        }}
      >
        <div
          style={{
            color: "#8b949e",
            fontSize: 11,
            letterSpacing: 1,
            fontWeight: 600,
          }}
        >
          CURRENT MISSION
        </div>
        <div
          style={{
            color: "#cdd9e5",
            fontSize: 15,
            fontWeight: 700,
            marginTop: 6,
          }}
        >
          {isActive
            ? data.running_sop_name
            : data.status === "OFFLINE"
              ? "等待後端連線"
              : "STANDBY (IDLE)"}
        </div>
        <div style={{ color: "#8b949e", fontSize: 12, marginTop: 4 }}>
          {data.description}
        </div>
      </div>

      {/* ── 溫濕度卡片 ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
          gap: 20,
          marginBottom: 24,
        }}
      >
        <div style={{ ...card, borderLeft: "3px solid #ff7b72" }}>
          <div
            style={{
              color: "#8b949e",
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: 1,
            }}
          >
            TEMP PV
          </div>
          <div
            style={{
              fontSize: 64,
              fontWeight: 800,
              color: "#ff7b72",
              lineHeight: 1.1,
              textAlign: "right",
            }}
          >
            {data.temperature.toFixed(2)}
            <span style={{ fontSize: 20, color: "#484f58", marginLeft: 5 }}>
              °C
            </span>
          </div>
        </div>

        <div style={{ ...card, borderLeft: "3px solid #a5d6ff" }}>
          <div
            style={{
              color: "#8b949e",
              fontSize: 11,
              fontWeight: 600,
              letterSpacing: 1,
            }}
          >
            HUMI PV
          </div>
          <div
            style={{
              fontSize: 64,
              fontWeight: 800,
              color: "#a5d6ff",
              lineHeight: 1.1,
              textAlign: "right",
            }}
          >
            {data.humidity.toFixed(1)}
            <span style={{ fontSize: 20, color: "#484f58", marginLeft: 5 }}>
              %
            </span>
          </div>
        </div>
      </div>

      {/* ── 趨勢圖 ── */}
      <div style={{ ...card, marginBottom: 24 }}>
        <div
          style={{
            color: "#8b949e",
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            marginBottom: 16,
          }}
        >
          TEMP / HUMI TREND（最近 60 秒）
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart
            data={history}
            margin={{ top: 5, right: 16, left: -10, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#21262d"
              vertical={false}
            />
            <XAxis
              dataKey="time"
              stroke="#30363d"
              tick={{ fontSize: 10, fill: "#484f58" }}
              hide={history.length < 2}
            />
            <YAxis
              stroke="#30363d"
              domain={["auto", "auto"]}
              tick={{ fontSize: 10, fill: "#484f58" }}
            />
            <Tooltip
              contentStyle={{
                background: "#161b22",
                border: "1px solid #30363d",
                fontSize: 11,
              }}
              itemStyle={{ color: "#cdd9e5" }}
            />
            <Line
              type="monotone"
              dataKey="temperature"
              name="溫度 (°C)"
              stroke="#ff7b72"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="humidity"
              name="濕度 (%RH)"
              stroke="#a5d6ff"
              strokeWidth={1.5}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* ── 執行紀錄列表 ── */}
      <div style={card}>
        <div
          style={{
            color: "#8b949e",
            fontSize: 11,
            fontWeight: 600,
            letterSpacing: 1,
            marginBottom: 16,
          }}
        >
          執行紀錄 EXECUTION HISTORY
        </div>
        {executions.length === 0 ? (
          <div
            style={{
              color: "#484f58",
              fontSize: 13,
              textAlign: "center",
              padding: "20px 0",
            }}
          >
            尚無執行紀錄
          </div>
        ) : (
          <table
            style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}
          >
            <thead>
              <tr style={{ borderBottom: "1px solid #30363d" }}>
                {["ID", "SOP ID", "執行時間", "報告"].map((h) => (
                  <th
                    key={h}
                    style={{
                      padding: "6px 12px",
                      textAlign: "left",
                      color: "#8b949e",
                      fontWeight: 600,
                    }}
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {executions.map((ex) => (
                <tr key={ex.id} style={{ borderBottom: "1px solid #21262d" }}>
                  <td style={{ padding: "8px 12px", color: "#484f58" }}>
                    #{ex.id}
                  </td>
                  <td
                    style={{
                      padding: "8px 12px",
                      color: "#cdd9e5",
                      fontFamily: "monospace",
                    }}
                  >
                    {ex.sop_id}
                  </td>
                  <td style={{ padding: "8px 12px", color: "#8b949e" }}>
                    {ex.created_at}
                  </td>
                  <td style={{ padding: "8px 12px" }}>
                    <button
                      onClick={() =>
                        window.open(`${API}/api/reports/csv/${ex.id}`, "_blank")
                      }
                      style={{
                        padding: "4px 10px",
                        background: "#1f6feb",
                        color: "#fff",
                        border: "none",
                        borderRadius: 4,
                        cursor: "pointer",
                        fontSize: 11,
                        fontWeight: 600,
                      }}
                    >
                      📥 CSV
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
};

export default Dashboard;
