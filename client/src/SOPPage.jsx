import React, { useState, useEffect } from 'react';

const SOPPage = () => {
  const [sops, setSops] = useState([]);
  const [statusData, setStatusData] = useState({ status: "IDLE", running_sop_name: "None" });

  useEffect(() => {
    fetch("http://localhost:8000/api/sop").then(res => res.json()).then(data => setSops(data));
    const timer = setInterval(() => {
      fetch("http://localhost:8000/api/latest").then(res => res.json()).then(data => setStatusData(data));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleControl = async (type) => {
    await fetch(`http://localhost:8000/api/stop/${type}`, { method: 'POST' });
  };

  const handleStart = async (sopId) => {
    await fetch(`http://localhost:8000/api/sop/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sop_id: sopId }),
    });
  };

  return (
    <div style={containerStyle}>
      {/* 頂部控制面板 - 核心修正：響應式佈局 */}
      <div style={panelStyle}>
        <div style={infoAreaStyle}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ ...statusDot, backgroundColor: getStatusColor(statusData.status) }} />
            <h2 style={{ margin: 0, fontSize: '1.2rem' }}>系統狀態: {statusData.status}</h2>
          </div>
          <p style={missionTextStyle}>當前任務: {statusData.running_sop_name}</p>
        </div>
        
        {/* 按鈕組 - 使用網格佈局防止擠壓 */}
        <div style={buttonGroupStyle}>
          <button onClick={() => handleControl('pause')} style={btnStyle("#ffaa00", "#000")}>⏸️ 暫停切換</button>
          <button onClick={() => handleControl('normal')} style={btnStyle("#444", "#fff")}>⏹️ 正常停止</button>
          <button onClick={() => handleControl('emergency')} style={btnStyle("#ff4d4d", "#fff")}>🚨 緊急停止</button>
        </div>
      </div>

      {/* SOP 列表 */}
      <div style={gridStyle}>
        {sops.map((sop) => (
          <div key={sop.sop_id} style={{ ...cardStyle, opacity: statusData.status === "RUNNING" ? 0.6 : 1 }}>
            <h3 style={{ margin: "0 0 10px 0", color: "#00d4ff" }}>{sop.name}</h3>
            <button 
              disabled={statusData.status === "RUNNING"}
              onClick={() => handleStart(sop.sop_id)}
              style={startBtnStyle(statusData.status === "RUNNING")}
            >
              {statusData.status === "RUNNING" ? "執行中鎖定" : "啟動測試程序"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// --- 優化後的樣式定義 ---

const containerStyle = {
  backgroundColor: "#050505", color: "#e0e0e0", 
  minHeight: "100vh", padding: "20px", boxSizing: "border-box"
};

const panelStyle = {
  background: "#111", padding: "20px", borderRadius: "12px", border: "1px solid #333",
  display: "flex", flexDirection: "row", flexWrap: "wrap", // 關鍵：寬度不足時自動換行
  justifyContent: "space-between", alignItems: "center", gap: "20px",
  marginBottom: "30px", boxShadow: "0 4px 15px rgba(0,0,0,0.5)"
};

const infoAreaStyle = {
  flex: "1 1 300px", // 最少佔用 300px，空間夠就撐開
  minWidth: "200px"
};

const statusDot = {
  width: "12px", height: "12px", borderRadius: "50%",
  boxShadow: "0 0 10px currentColor"
};

const missionTextStyle = {
  margin: "8px 0 0 0", color: "#888", fontSize: "0.9rem",
  whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" // 防止文字太長撐破 UI
};

const buttonGroupStyle = {
  display: "grid", 
  gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))", // 按鈕自動等分
  gap: "10px", flex: "1 1 400px" 
};

const gridStyle = {
  display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "20px"
};

const cardStyle = {
  background: "#111", padding: "20px", borderRadius: "12px", border: "1px solid #222"
};

const btnStyle = (bg, color) => ({
  backgroundColor: bg, color: color, border: "none", padding: "12px 5px", 
  borderRadius: "6px", fontWeight: "bold", cursor: "pointer", fontSize: "0.85rem",
  textAlign: "center"
});

const startBtnStyle = (locked) => ({
  width: "100%", padding: "12px", borderRadius: "8px", border: "none",
  fontWeight: "bold", cursor: locked ? "not-allowed" : "pointer",
  backgroundColor: locked ? "#222" : "#00d4ff",
  color: locked ? "#555" : "#000", marginTop: "10px"
});

const getStatusColor = (s) => {
  if (s === "RUNNING") return "#00ff00";
  if (s === "PAUSED") return "#ffaa00";
  if (s === "FINISHING") return "#00d4ff";
  return "#555";
};

export default SOPPage;