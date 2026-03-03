import React, { useState, useEffect } from "react";
import axios from "axios";
import "./SOPPage.css";

const SAFETY_CHECKS = [
  "測試孔是否用塑膠塞及抹布將兩邊塞緊，以免水氣跑出。",
  "線材類治具等移至上方後再塞，以免水氣往利用線材類治具流至設備上造成毀損。",
  "抹布末端勿留至 Sample 上，以免低溫轉高溫時水氣流至 Sample 上導致燒燬。",
  "電源頭請放在治具、線材類上或懸空在鐵架下方，勿放在鐵架上。",
];

// 只有这两个状态才显示执行画面
const ACTIVE_STATUSES = ["RUNNING", "PAUSED"];

const SOPPage = () => {
  const [safetyChecked, setSafetyChecked] = useState([
    false,
    false,
    false,
    false,
  ]);
  const allChecked = safetyChecked.every(Boolean);
  const [testMethods, setTestMethods] = useState([]);
  const [data, setData] = useState({
    status: "OFFLINE",
    temperature: 0.0,
    humidity: 0.0,
    running_sop_name: "None",
    description: "等待連線...",
    timestamp: "--:--:--",
  });
  const [activeSop, setActiveSop] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({});

  const isActive = ACTIVE_STATUSES.includes(data.status);

  useEffect(() => {
    const fetchSOPs = async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/sop/");
        setTestMethods(res.data);
      } catch (err) {
        console.error("Failed to fetch SOPs:", err);
      }
    };
    fetchSOPs();
  }, []);

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

  const handleAction = async (type) => {
    await axios.post(`http://localhost:8000/api/stop/${type}`);
    if (type === "normal" || type === "emergency") {
      setActiveSop(null);
      setCompletedSteps({});
    }
  };

  const startSop = async (sop) => {
    try {
      await axios.post("http://localhost:8000/api/sop/start", {
        sop_id: sop.sop_id,
        device_id: "KSON_CH01",
        standard_id: sop.standard_id,
      });
      setActiveSop(sop);
      // ✅ 启动时自动勾选 Step 1 和 Step 2
      setCompletedSteps({ 1: true, 2: true });
    } catch (err) {
      alert("啟動程序失敗");
    }
  };

  const completedCount = Object.values(completedSteps).filter(Boolean).length;
  const totalSteps = activeSop ? activeSop.steps.length : 0;
  const allStepsDone = activeSop && completedCount === totalSteps;

  return (
    <div className="sop-page-layout">
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
            {isActive ? data.running_sop_name || "執行中" : "STANDBY (IDLE)"}
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

      <main className="control-side">
        <div className="scroll-wrapper">
          <section className="operation-box">
            <div className="box-header">
              <span className="pulse-icon"></span>
              <h2>系統控制面板</h2>
            </div>
            <p className="task-desc">{data.description || "等待數據載入..."}</p>
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

          {isActive && activeSop && (
            <section
              className="operation-box"
              style={{ borderLeft: "4px solid #58a6ff" }}
            >
              <div className="box-header">
                <span>📋</span>
                <h2>{activeSop.name} - 執行步驟</h2>
              </div>
              <p
                style={{
                  color: "#8b949e",
                  fontSize: "13px",
                  marginBottom: "12px",
                }}
              >
                請依序確認每個步驟已完成：
              </p>
              {activeSop.steps.map((step) => (
                <label
                  key={step.step_id}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: "10px",
                    marginBottom: "12px",
                    cursor: "pointer",
                    color: completedSteps[step.step_id] ? "#57ab5a" : "#cdd9e5",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={!!completedSteps[step.step_id]}
                    onChange={() => {
                      setCompletedSteps((prev) => ({
                        ...prev,
                        [step.step_id]: !prev[step.step_id],
                      }));
                    }}
                    style={{ marginTop: "3px", accentColor: "#57ab5a" }}
                  />
                  <div>
                    <div style={{ fontWeight: "bold" }}>
                      Step {step.step_id}. {step.name}
                    </div>
                    <div
                      style={{
                        fontSize: "12px",
                        color: "#8b949e",
                        marginTop: "2px",
                      }}
                    >
                      {step.description}
                    </div>
                  </div>
                </label>
              ))}
              <p
                style={{
                  color: allStepsDone ? "#57ab5a" : "#8b949e",
                  fontSize: "12px",
                  marginTop: "8px",
                }}
              >
                {completedCount} / {totalSteps} 步驟完成
                {allStepsDone && " ✅ 所有步驟已完成！"}
              </p>
            </section>
          )}

          {!isActive && (
            <>
              <section
                className="operation-box"
                style={{ borderLeft: "4px solid #f0a500" }}
              >
                <div className="box-header">
                  <span>⚠️</span>
                  <h2>上架驗證注意事項</h2>
                </div>
                <p
                  style={{
                    color: "#8b949e",
                    fontSize: "13px",
                    marginBottom: "12px",
                  }}
                >
                  啟動測試前，請確認以下所有項目：
                </p>
                {SAFETY_CHECKS.map((item, index) => (
                  <label
                    key={index}
                    style={{
                      display: "flex",
                      alignItems: "flex-start",
                      gap: "10px",
                      marginBottom: "10px",
                      cursor: "pointer",
                      color: safetyChecked[index] ? "#57ab5a" : "#cdd9e5",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={safetyChecked[index]}
                      onChange={() => {
                        const updated = [...safetyChecked];
                        updated[index] = !updated[index];
                        setSafetyChecked(updated);
                      }}
                      style={{ marginTop: "3px", accentColor: "#57ab5a" }}
                    />
                    {index + 1}. {item}
                  </label>
                ))}
                {!allChecked ? (
                  <p
                    style={{
                      color: "#f0a500",
                      fontSize: "12px",
                      marginTop: "8px",
                    }}
                  >
                    ⚠️ 請確認所有注意事項後才能啟動測試
                  </p>
                ) : (
                  <p
                    style={{
                      color: "#57ab5a",
                      fontSize: "12px",
                      marginTop: "8px",
                    }}
                  >
                    ✅ 所有注意事項已確認，可以啟動測試
                  </p>
                )}
              </section>

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
                        disabled={!allChecked}
                      >
                        {!allChecked ? "請先確認注意事項" : "啟動測試程序"}
                      </button>
                    </div>
                  ))
                ) : (
                  <p style={{ color: "#8b949e" }}>正在加載測試程序...</p>
                )}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default SOPPage;
