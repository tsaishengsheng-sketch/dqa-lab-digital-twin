import React, { useState, useEffect } from "react";
import axios from "axios";
import "./SOPPage.css";

const API = "http://localhost:8000";

const SAFETY_CHECKS = [
  "測試孔是否用塑膠塞及抹布將兩邊塞緊，以免水氣跑出。",
  "線材類治具等移至上方後再塞，以免水氣往利用線材類治具流至設備上造成毀損。",
  "抹布末端勿留至 Sample 上，以免低溫轉高溫時水氣流至 Sample 上導致燒燬。",
  "電源頭請放在治具、線材類上或懸空在鐵架下方，勿放在鐵架上。",
];

const ACTIVE_STATUSES = ["RUNNING", "PAUSED"];

// ─── 測試條件摘要卡 ───────────────────────────────────────────
const ConditionCard = ({ test }) => {
  if (!test) return null;
  const rows = [
    [
      "高溫上限",
      test.high_temperature != null ? `${test.high_temperature} °C` : "—",
    ],
    [
      "低溫下限",
      test.low_temperature != null ? `${test.low_temperature} °C` : "—",
    ],
    ["升降溫速率", `${test.ramp_rate} °C/min`],
    ["停留時間", `${test.dwell_time_hours} h`],
    ["循環次數", test.cycles ?? "—"],
    [
      "濕度設定",
      test.humidity_rh_percent != null
        ? `${test.humidity_rh_percent} %RH`
        : "N/A",
    ],
    ["通電狀態", test.power_on ? "通電 (Powered)" : "非通電 (Unpowered)"],
    ["溫度容差", `± ${test.temp_tolerance} °C`],
    ["濕度容差", `± ${test.humi_tolerance} %RH`],
  ];
  return (
    <div
      style={{
        background: "#0d1117",
        border: "1px solid #30363d",
        borderLeft: "3px solid #a371f7",
        borderRadius: 8,
        padding: "14px 16px",
        marginTop: 12,
      }}
    >
      <div
        style={{
          fontSize: 11,
          color: "#a371f7",
          fontWeight: 700,
          marginBottom: 6,
          letterSpacing: 1,
        }}
      >
        📋 測試條件摘要
      </div>
      <div
        style={{
          fontSize: 11,
          color: "#8b949e",
          marginBottom: 10,
          lineHeight: 1.5,
        }}
      >
        {test.description}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "3px 12px",
        }}
      >
        {rows.map(([label, value]) => (
          <div
            key={label}
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "4px 0",
              borderBottom: "1px solid #21262d",
            }}
          >
            <span style={{ color: "#8b949e", fontSize: 11 }}>{label}</span>
            <span style={{ color: "#cdd9e5", fontSize: 11, fontWeight: 600 }}>
              {value}
            </span>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 10, fontSize: 10, color: "#484f58" }}>
        📖 {test.reference}
      </div>
    </div>
  );
};

// ─── 選擇按鈕組 ───────────────────────────────────────────────
const SelectGroup = ({ step, title, items, selected, onSelect, accent }) => {
  const isDone = !!selected;
  return (
    <div style={{ marginBottom: 16 }}>
      {/* 標題列 */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          marginBottom: 10,
        }}
      >
        <div
          style={{
            width: 22,
            height: 22,
            borderRadius: "50%",
            flexShrink: 0,
            background: isDone ? accent : "#21262d",
            border: `2px solid ${isDone ? accent : "#30363d"}`,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 11,
            fontWeight: 800,
            color: isDone ? "#0d1117" : "#8b949e",
            transition: "all .2s",
          }}
        >
          {isDone ? "✓" : step}
        </div>
        <span
          style={{
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: 0.5,
            color: isDone ? "#cdd9e5" : "#8b949e",
          }}
        >
          {title}
        </span>
      </div>

      {/* 選項按鈕 */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {items.map(([key, label]) => {
          const active = selected === key;
          return (
            <button
              key={key}
              onClick={() => onSelect(key)}
              style={{
                padding: "6px 12px",
                borderRadius: 6,
                fontSize: 11,
                cursor: "pointer",
                transition: "all .15s",
                border: `1px solid ${active ? accent : "#30363d"}`,
                background: active ? `${accent}22` : "#161b22",
                color: active ? accent : "#8b949e",
                fontWeight: active ? 700 : 400,
                whiteSpace: "nowrap",
              }}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// ─── 主元件 ───────────────────────────────────────────────────
const SOPPage = () => {
  // ── 即時數據 ──
  const [data, setData] = useState({
    status: "OFFLINE",
    temperature: 0.0,
    humidity: 0.0,
    running_sop_name: "None",
    description: "等待連線...",
    timestamp: "--:--:--",
  });

  // ── 三層選擇 ──
  const [standardTree, setStandardTree] = useState({});
  const [selectedStd, setSelectedStd] = useState(null);
  const [selectedVer, setSelectedVer] = useState(null);
  const [selectedTest, setSelectedTest] = useState(null);

  // ── 執行狀態 ──
  const [activeSop, setActiveSop] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({});
  const [savedExecutionId, setSavedExecutionId] = useState(null);
  const [safetyChecked, setSafetyChecked] = useState([
    false,
    false,
    false,
    false,
  ]);

  // ── 衍生值 ──
  const isActive = ACTIVE_STATUSES.includes(data.status);
  const allChecked = safetyChecked.every(Boolean);
  const totalSteps = activeSop?.steps?.length ?? 0;
  const doneCnt = Object.values(completedSteps).filter(Boolean).length;
  const allStepsDone = activeSop && doneCnt === totalSteps;

  const stdData = selectedStd ? standardTree[selectedStd] : null;
  const verData = selectedVer ? stdData?.versions?.[selectedVer] : null;
  const testData = selectedTest ? verData?.tests?.[selectedTest] : null;

  const versionItems = stdData
    ? Object.entries(stdData.versions).map(([k, v]) => [k, v.label])
    : [];
  const testItems = verData
    ? Object.entries(verData.tests).map(([k, v]) => [k, v.name])
    : [];

  // ── API ──
  useEffect(() => {
    axios
      .get(`${API}/api/sop/standards/tree`)
      .then((r) => setStandardTree(r.data))
      .catch((e) => console.error("Failed to load standards tree", e));
  }, []);

  useEffect(() => {
    const t = setInterval(() => {
      axios
        .get(`${API}/api/latest`)
        .then((r) => setData(r.data))
        .catch(() => {});
    }, 1000);
    return () => clearInterval(t);
  }, []);

  // 切換法規時清除下層選擇
  const handleSelectStd = (key) => {
    setSelectedStd(key);
    setSelectedVer(null);
    setSelectedTest(null);
  };
  const handleSelectVer = (key) => {
    setSelectedVer(key);
    setSelectedTest(null);
  };

  // ── 啟動測試 ──
  const startSop = async () => {
    if (!testData) return;
    try {
      // 1. 啟動 SOP
      await axios.post(`${API}/api/sop/start`, {
        sop_id: testData.sop_id,
        device_id: "KSON_CH01",
      });

      // 2. 從 /api/sop/ 拿完整步驟清單（tree API 不含 steps）
      let steps = [];
      try {
        const sopList = await axios.get(`${API}/api/sop/`);
        const full = sopList.data.find((s) => s.sop_id === testData.sop_id);
        if (full && Array.isArray(full.steps) && full.steps.length > 0) {
          steps = full.steps;
        }
      } catch {
        /* 撈不到就用備案 */
      }

      // 3. 撈不到時的備案步驟
      if (steps.length === 0) {
        steps = [
          {
            step_id: 1,
            name: "設備開機與預檢",
            description: "確認電源、保險絲、水箱水位正常，記錄初始外觀狀態。",
            optional: false,
          },
          {
            step_id: 2,
            name: "設定測試參數",
            description: "確認目標溫度、速率、時間等參數已正確設定。",
            optional: false,
          },
          {
            step_id: 3,
            name: "啟動並監控測試",
            description: "按下 RUN 鍵，監控溫度曲線是否正常。",
            optional: false,
          },
          {
            step_id: 4,
            name: "測試完成確認",
            description: "確認測試完成，設備無異常，拍照記錄。",
            optional: false,
          },
          {
            step_id: 5,
            name: "儲存測試紀錄",
            description: "點擊儲存按鈕，下載 CSV 測試報告。",
            optional: false,
          },
        ];
      }

      setActiveSop({ ...testData, steps });
      setCompletedSteps({ 1: true, 2: true }); // 前兩步自動勾選
      setSavedExecutionId(null);
    } catch {
      alert("啟動程序失敗，請確認後端是否正常運作。");
    }
  };

  // ── 系統控制 ──
  const handleAction = async (type) => {
    await axios.post(`${API}/api/stop/${type}`);
    if (type === "normal" || type === "emergency") {
      setActiveSop(null);
      setCompletedSteps({});
      setSavedExecutionId(null);
      setSafetyChecked([false, false, false, false]);
    }
  };

  // ── 儲存紀錄 ──
  const saveExecution = async () => {
    try {
      const steps = activeSop.steps.map((s) => ({
        step_id: s.step_id,
        completed: !!completedSteps[s.step_id],
        parameters: null,
      }));
      const res = await axios.post(`${API}/api/sop-executions/`, {
        sop_id: activeSop.sop_id,
        steps,
      });
      setSavedExecutionId(res.data.id);
    } catch {
      alert("❌ 儲存失敗，請確認後端連線。");
    }
  };

  const downloadReport = () =>
    window.open(`${API}/api/reports/csv/${savedExecutionId}`, "_blank");

  // ─────────────────────────────────────────────────────────────
  return (
    <div className="sop-page-layout">
      {/* ══ 左側：監控區 (40%) ══ */}
      <aside className="monitor-side">
        <div className="brand-box">
          <h1 className="main-title">KSON AICM | Digital Twin</h1>
          <div className="status-row">
            <span className={`status-dot ${data.status.toLowerCase()}`} />
            <span className="status-label">{data.status}</span>
            <span className="update-time">{data.timestamp}</span>
          </div>
        </div>

        <div className="info-card highlight">
          <label>CURRENT MISSION</label>
          <div className="value-large" style={{ fontSize: 13 }}>
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

      {/* ══ 右側：操作區 (60%) ══ */}
      <main className="control-side">
        <div className="scroll-wrapper">
          {/* ── 系統控制（永遠顯示）── */}
          <section className="operation-box">
            <div className="box-header">
              <span className="pulse-icon" />
              <h2>系統控制面板</h2>
            </div>
            <p className="task-desc">{data.description}</p>
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

          {/* ══ 執行中：步驟清單 ══ */}
          {isActive && activeSop && (
            <section
              className="operation-box"
              style={{ borderLeft: "3px solid #58a6ff" }}
            >
              <div className="box-header">
                <span>📋</span>
                <h2 style={{ fontSize: 13 }}>{activeSop.name}</h2>
              </div>
              <p style={{ color: "#8b949e", fontSize: 12, marginBottom: 14 }}>
                請依序確認每個步驟已完成：
              </p>

              {(activeSop.steps || []).map((step) => (
                <label
                  key={step.step_id}
                  style={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 10,
                    marginBottom: 12,
                    cursor: "pointer",
                    color: completedSteps[step.step_id] ? "#57ab5a" : "#cdd9e5",
                  }}
                >
                  <input
                    type="checkbox"
                    checked={!!completedSteps[step.step_id]}
                    onChange={() =>
                      setCompletedSteps((p) => ({
                        ...p,
                        [step.step_id]: !p[step.step_id],
                      }))
                    }
                    style={{
                      marginTop: 3,
                      accentColor: "#57ab5a",
                      flexShrink: 0,
                    }}
                  />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 12 }}>
                      Step {step.step_id}. {step.name}
                      {step.optional && (
                        <span
                          style={{
                            marginLeft: 6,
                            fontSize: 10,
                            padding: "1px 6px",
                            background: "#21262d",
                            color: "#8b949e",
                            borderRadius: 4,
                          }}
                        >
                          Optional
                        </span>
                      )}
                    </div>
                    <div
                      style={{ fontSize: 11, color: "#8b949e", marginTop: 2 }}
                    >
                      {step.description}
                    </div>
                  </div>
                </label>
              ))}

              <div
                style={{
                  color: allStepsDone ? "#57ab5a" : "#8b949e",
                  fontSize: 12,
                  marginTop: 4,
                }}
              >
                {doneCnt} / {totalSteps} 步驟完成{allStepsDone && " ✅"}
              </div>

              {/* 儲存按鈕 */}
              {allStepsDone && !savedExecutionId && (
                <button
                  onClick={saveExecution}
                  style={{
                    marginTop: 12,
                    width: "100%",
                    padding: "10px",
                    background: "#238636",
                    color: "#fff",
                    border: "none",
                    borderRadius: 6,
                    cursor: "pointer",
                    fontWeight: 700,
                    fontSize: 14,
                  }}
                >
                  💾 儲存執行紀錄
                </button>
              )}

              {/* 已儲存 + 下載 */}
              {savedExecutionId && (
                <div
                  style={{
                    marginTop: 12,
                    display: "flex",
                    flexDirection: "column",
                    gap: 8,
                  }}
                >
                  <div
                    style={{
                      padding: 10,
                      background: "#0f2318",
                      color: "#57ab5a",
                      borderRadius: 6,
                      fontSize: 13,
                      textAlign: "center",
                      fontWeight: 700,
                    }}
                  >
                    ✅ 紀錄已儲存（ID: {savedExecutionId}）
                  </div>
                  <button
                    onClick={downloadReport}
                    style={{
                      padding: "10px",
                      background: "#1f6feb",
                      color: "#fff",
                      border: "none",
                      borderRadius: 6,
                      cursor: "pointer",
                      fontWeight: 700,
                      fontSize: 14,
                    }}
                  >
                    📥 下載 CSV 測試報告（ISO 17025）
                  </button>
                </div>
              )}
            </section>
          )}

          {/* ══ 待機中：三步驟選擇器 ══ */}
          {!isActive && (
            <>
              <section
                className="operation-box"
                style={{ borderLeft: "3px solid #58a6ff" }}
              >
                <div className="box-header">
                  <span>🔬</span>
                  <h2>選擇測試標準</h2>
                </div>

                {/* Step 1：法規 */}
                <SelectGroup
                  step={1}
                  title="選擇法規"
                  accent="#58a6ff"
                  items={Object.entries(standardTree).map(([k, v]) => [
                    k,
                    v.label,
                  ])}
                  selected={selectedStd}
                  onSelect={handleSelectStd}
                />

                {/* Step 2：版本（有法規才顯示） */}
                {stdData && (
                  <>
                    <div
                      style={{
                        borderTop: "1px solid #21262d",
                        margin: "4px 0 14px",
                      }}
                    />
                    <div
                      style={{
                        fontSize: 11,
                        color: "#8b949e",
                        marginBottom: 10,
                        lineHeight: 1.5,
                      }}
                    >
                      {stdData.description}
                    </div>
                    <SelectGroup
                      step={2}
                      title="選擇版本 / Class"
                      accent="#f0a500"
                      items={versionItems}
                      selected={selectedVer}
                      onSelect={handleSelectVer}
                    />
                  </>
                )}

                {/* Step 3：測試條件（有版本才顯示） */}
                {verData && (
                  <>
                    <div
                      style={{
                        borderTop: "1px solid #21262d",
                        margin: "4px 0 14px",
                      }}
                    />
                    <div
                      style={{
                        fontSize: 11,
                        color: "#8b949e",
                        marginBottom: 10,
                        lineHeight: 1.5,
                      }}
                    >
                      {verData.description}
                    </div>
                    <SelectGroup
                      step={3}
                      title="選擇測試條件"
                      accent="#57ab5a"
                      items={testItems}
                      selected={selectedTest}
                      onSelect={setSelectedTest}
                    />
                  </>
                )}

                {/* 測試條件摘要卡（有測試條件才顯示） */}
                {testData && <ConditionCard test={testData} />}
              </section>

              {/* ── 注意事項 + 啟動按鈕（選完測試條件才顯示）── */}
              {testData && (
                <section
                  className="operation-box"
                  style={{ borderLeft: "3px solid #f0a500" }}
                >
                  <div className="box-header">
                    <span>⚠️</span>
                    <h2>上架驗證注意事項</h2>
                  </div>
                  <p
                    style={{ color: "#8b949e", fontSize: 12, marginBottom: 14 }}
                  >
                    啟動測試前，請確認以下所有項目：
                  </p>

                  {SAFETY_CHECKS.map((item, i) => (
                    <label
                      key={i}
                      style={{
                        display: "flex",
                        alignItems: "flex-start",
                        gap: 10,
                        marginBottom: 10,
                        cursor: "pointer",
                        color: safetyChecked[i] ? "#57ab5a" : "#cdd9e5",
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={safetyChecked[i]}
                        onChange={() => {
                          const u = [...safetyChecked];
                          u[i] = !u[i];
                          setSafetyChecked(u);
                        }}
                        style={{
                          marginTop: 3,
                          accentColor: "#57ab5a",
                          flexShrink: 0,
                        }}
                      />
                      <span style={{ fontSize: 12 }}>
                        {i + 1}. {item}
                      </span>
                    </label>
                  ))}

                  {allChecked ? (
                    <p style={{ color: "#57ab5a", fontSize: 12, marginTop: 6 }}>
                      ✅ 所有注意事項已確認，可以啟動測試
                    </p>
                  ) : (
                    <p style={{ color: "#f0a500", fontSize: 12, marginTop: 6 }}>
                      ⚠️ 請確認所有注意事項後才能啟動測試
                    </p>
                  )}

                  <button
                    onClick={startSop}
                    disabled={!allChecked}
                    style={{
                      marginTop: 14,
                      width: "100%",
                      padding: "12px",
                      background: allChecked ? "#238636" : "#21262d",
                      color: allChecked ? "#fff" : "#484f58",
                      border: `1px solid ${allChecked ? "#2ea043" : "#30363d"}`,
                      borderRadius: 6,
                      cursor: allChecked ? "pointer" : "not-allowed",
                      fontWeight: 700,
                      fontSize: 14,
                      transition: "all .2s",
                    }}
                  >
                    {allChecked
                      ? `🚀 啟動測試：${testData.name}`
                      : "請先確認所有注意事項"}
                  </button>
                </section>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default SOPPage;
