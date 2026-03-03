import React, { useState, useEffect } from "react";
import axios from "axios";
import "./SOPPage.css";

const SOPPage = () => {
  // SOP 列表從後端動態獲取
  const [testMethods, setTestMethods] = useState([]);

  // 即時狀態 State
  const [data, setData] = useState({
    status: "OFFLINE",
    temperature: 0.0,
    humidity: 0.0,
    running_sop_name: "None",
    description: "等待連線...",
    timestamp: "--:--:--",
  });

  // 啟動時獲取 SOP 列表
  useEffect(() => {
    const fetchSOPs = async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/sop/");
        setTestMethods(res.data);
        console.log(`✅ Loaded ${res.data.length} SOPs from backend`);
      } catch (err) {
        console.error("Failed to fetch SOPs:", err);
      }
    };

    fetchSOPs();
  }, []);

  // 每秒輪詢後端 API
  useEffect(() => {
    const timer = setInterval(async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/latest");
        setData(res.data);
      } catch (err) {
        console.error("API 連線失敗");
      }
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 控制功能
  const handleAction = async (type) => {
    await axios.post(`http://localhost:8000/api/stop/${type}`);
  };

  // ✅ 直接用后端传过来的 standard_id
  const startSop = async (sop) => {
    try {
      await axios.post("http://localhost:8000/api/sop/start", {
        sop_id: sop.sop_id,
        device_id: "KSON_CH01",
        standard_id: sop.standard_id, // ← 直接用，不用查表
      });
    } catch (err) {
      alert("啟動程序失敗");
    }
  };

  return (
    <div className="sop-page-layout">
      {/* 左側：數據監控區域 (40%) */}
      <aside className="monitor-side">
        <div className="brand-box">
          <h1 className="main-title">KSON AICM | Digital Twin</h1>
          <div className="status-row">
            <span className={`status-dot ${data.status.toLowerCase()}`}></span>
            <span className="status-label">{data.status}</span>
            <span className="update-time">{data.timestamp}</span>
          </div>
        </div>

        <div className="info-card highlight">
          <label>CURRENT MISSION</label>
          <div className="value-large">
            {data.status === "IDLE"
              ? "STANDBY (IDLE)"
              : data.running_sop_name || "Disconnected"}
          </div>
        </div>

        <div className="info-card temp-card">
          <label>TEMP PV</label>
          <div className="value-pv">
            {data.temperature.toFixed(2)}
            <span className="unit">°C</span>
          </div>
        </div>

        <div className="info-card humi-card">
          <label>HUMI PV</label>
          <div className="value-pv">
            {data.humidity.toFixed(1)}
            <span className="unit">%</span>
          </div>
        </div>
      </aside>

      {/* 右側：操作執行區域 (60%) */}
      <main className="control-side">
        <div className="scroll-wrapper">
          {/* 系統操作按鈕 */}
          <section className="operation-box">
            <div className="box-header">
              <span className="pulse-icon"></span>
              <h2>系統控制面板</h2>
            </div>
            <p className="task-desc">
              當前詳情: {data.description || "等待數據載入..."}
            </p>

            <div className="btn-group-row">
              <button
                className="ctrl-btn amber"
                onClick={() => handleAction("pause")}
              >
                ⏸ 暫停切換
              </button>
              <button
                className="ctrl-btn grey"
                onClick={() => handleAction("normal")}
              >
                ⏹ 正常停止
              </button>
              <button
                className="ctrl-btn red"
                onClick={() => handleAction("emergency")}
              >
                🚨 緊急停止
              </button>
            </div>
          </section>

          {/* SOP 列表區 */}
          <div className="sop-list-container">
            <h3 className="list-label">
              可用測試程序 (SOP List) - {testMethods.length} 個
            </h3>
            {testMethods.length > 0 ? (
              testMethods.map((sop) => (
                <div key={sop.sop_id} className="sop-item-card">
                  <h3 className="sop-name">{sop.name}</h3>
                  <p className="sop-desc">{sop.test_type}</p>
                  <button
                    className="btn-launch"
                    onClick={() => startSop(sop)}
                    disabled={data.status === "RUNNING"}
                  >
                    {data.status === "RUNNING" ? "程序執行中" : "啟動測試程序"}
                  </button>
                </div>
              ))
            ) : (
              <p style={{ color: "#8b949e" }}>正在加載測試程序...</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default SOPPage;
