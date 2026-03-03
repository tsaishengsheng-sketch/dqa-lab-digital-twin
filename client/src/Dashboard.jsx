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

// 各狀態對應顏色
const STATUS_COLORS = {
  RUNNING: "#00ff00",
  PAUSED: "#f0a500",
  FINISHING: "#58a6ff",
  EMERGENCY: "#ff4444",
  IDLE: "#888888",
  OFFLINE: "#666666",
};

const Dashboard = () => {
  const [data, setData] = useState({
    temperature: 0,
    humidity: 0,
    status: "OFFLINE",
    timestamp: "--:--:--",
    running_sop_name: "None",
  });
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/latest");
        const json = res.data;
        if (json.temperature !== undefined) {
          setData(json);
          setHistory((prev) => [
            ...prev.slice(-29),
            { ...json, time: json.timestamp },
          ]);
        }
      } catch (err) {
        console.error("Fetch Error:", err);
      }
    };

    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = STATUS_COLORS[data.status] || "#666666";
  const isActive = ["RUNNING", "FINISHING", "PAUSED", "EMERGENCY"].includes(
    data.status,
  );

  return (
    <div
      style={{
        backgroundColor: "#050505",
        color: "#e0e0e0",
        minHeight: "100vh",
        padding: "20px",
        fontFamily: "monospace",
        boxSizing: "border-box",
        width: "100%",
      }}
    >
      {/* 標題欄 */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          borderBottom: "2px solid #222",
          paddingBottom: "10px",
          gap: "10px",
        }}
      >
        <h1
          style={{
            color: "#00d4ff",
            margin: 0,
            fontSize: "clamp(1.2rem, 5vw, 2rem)",
          }}
        >
          KSON AICM | Digital Twin
        </h1>
        <div style={{ textAlign: "right" }}>
          <span style={{ color: statusColor, fontWeight: "bold" }}>
            ● {data.status}
          </span>
          <div style={{ fontSize: "12px", color: "#666" }}>
            Updated: {data.timestamp}
          </div>
        </div>
      </div>

      {/* 當前任務 */}
      <div
        style={{
          marginTop: "20px",
          padding: "15px 20px",
          background: "linear-gradient(90deg, #111 0%, #080808 100%)",
          borderRadius: "8px",
          borderLeft: `4px solid ${statusColor}`,
          boxShadow: "0 4px 15px rgba(0,0,0,0.5)",
        }}
      >
        <div style={{ color: "#666", fontSize: "12px", letterSpacing: "1px" }}>
          CURRENT MISSION
        </div>
        <h2
          style={{
            color: isActive ? "#e0e0e0" : "#444",
            margin: "5px 0 0 0",
            fontSize: "1.5rem",
          }}
        >
          {isActive ? data.running_sop_name : "STANDBY (IDLE)"}
        </h2>
      </div>

      {/* 溫濕度卡片 */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(350px, 1fr))",
          gap: "25px",
          marginTop: "25px",
        }}
      >
        <div
          style={{
            background: "#111",
            padding: "25px",
            borderRadius: "12px",
            border: "1px solid #333",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{
              color: "#ff5500",
              fontSize: "1.1rem",
              width: "100%",
              marginBottom: "10px",
            }}
          >
            TEMP PV
          </div>
          <div
            style={{
              fontSize: "clamp(3.5rem, 12vw, 6rem)",
              fontWeight: "bold",
              color: "#ff5500",
              textShadow: "0 0 20px rgba(255,85,0,0.2)",
              lineHeight: 1,
            }}
          >
            {data.temperature.toFixed(2)}
            <span style={{ fontSize: "0.4em" }}>°C</span>
          </div>
        </div>

        <div
          style={{
            background: "#111",
            padding: "25px",
            borderRadius: "12px",
            border: "1px solid #333",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <div
            style={{
              color: "#00d4ff",
              fontSize: "1.1rem",
              width: "100%",
              marginBottom: "10px",
            }}
          >
            HUMI PV
          </div>
          <div
            style={{
              fontSize: "clamp(3.5rem, 12vw, 6rem)",
              fontWeight: "bold",
              color: "#00d4ff",
              textShadow: "0 0 20px rgba(0,212,255,0.2)",
              lineHeight: 1,
            }}
          >
            {data.humidity.toFixed(1)}
            <span style={{ fontSize: "0.4em" }}>%</span>
          </div>
        </div>
      </div>

      {/* 趨勢圖 */}
      <div
        style={{
          marginTop: "30px",
          background: "#111",
          padding: "20px",
          borderRadius: "12px",
          height: "350px",
          border: "1px solid #222",
          width: "100%",
          boxSizing: "border-box",
        }}
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={history}
            margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#222"
              vertical={false}
            />
            <XAxis
              dataKey="timestamp"
              stroke="#444"
              tick={{ fontSize: 10 }}
              hide={history.length < 2}
            />
            <YAxis
              stroke="#444"
              domain={["auto", "auto"]}
              tick={{ fontSize: 10 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#000",
                border: "1px solid #333",
                color: "#fff",
              }}
              itemStyle={{ fontSize: "12px" }}
            />
            <Line
              type="monotone"
              dataKey="temperature"
              stroke="#ff5500"
              strokeWidth={3}
              dot={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="humidity"
              stroke="#00d4ff"
              strokeWidth={2}
              dot={false}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Dashboard;
