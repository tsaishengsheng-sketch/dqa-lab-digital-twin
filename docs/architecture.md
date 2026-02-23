==============================================================
                              DQA LAB 數位雙生平台
                                 系統架構圖
==============================================================
📁 客戶端 (Browser) - React 前端模塊
├─ ✅ 儀表板 (Dashboard)
├─ ✅ SOP執行頁 (SOPPage)
├─ ⏳ 治具管理 (Fixtures)
├─ ⏳ 異常看板 (Issues)
├─ ⏳ Thermal 工作流 (Thermal)
├─ ⏳ 報告檢視 (Reports)
├─ ⏳ 專案管理 (Projects)
├─ ⏳ 設備管理 (Devices)
├─ ⏳ 知識庫 (Knowledge)
├─ ⏳ 使用者中心 (User)
└─ ⏳ 設定頁面 (Settings)

                                  │
                                  ▼ HTTP API (REST)
==============================================================
📁 後端 API 路由層 (FastAPI)
├─ ✅ /api/sop          - SOP 模板
├─ ✅ /api/sop-exec     - SOP 執行紀錄
├─ ✅ /api/latest       - 即時溫濕度
├─ ⏳ /api/fixtures     - 治具管理
├─ ⏳ /api/issues       - 異常追蹤
├─ ⏳ /api/thermal      - Thermal 工作流
├─ ⏳ /api/reports      - 報告生成
├─ ⏳ /api/projects     - 專案管理
├─ ⏳ /api/devices      - 設備管理
├─ ⏳ /api/auth         - 認證授權
└─ ⏳ /api/knowledge    - 知識庫

                                  │
                                  ▼ 業務服務層
==============================================================
📁 業務服務層 (Services)
├─ ✅ SOP管理        ✅ 執行紀錄        ✅ 即時數據(雛形)
├─ ⏳ 治具管理        ⏳ 異常追蹤        ⏳ Thermal工作流
├─ ⏳ 報告生成        ⏳ 專案管理        ⏳ 設備管理
├─ ⏳ 使用者認證      ⏳ 知識庫          ⏳ 郵件通知
├─ ⏳ 數據分析 (預測/相似檢索)
└─ ⏳ 稽核合規 (ISO 17025)

                                  │
                                  ▼ 資料存取 (ORM)
==============================================================
📁 資料庫模型層 (SQLite)
├─ ✅ device_data           ✅ sop_templates        ✅ sop_executions
├─ ✅ step_records
├─ ⏳ fixtures               ⏳ fixture_borrows       ⏳ issues
├─ ⏳ issue_actions          ⏳ thermal_records       ⏳ thermal_images
├─ ⏳ projects               ⏳ tasks                 ⏳ devices
├─ ⏳ device_calibrations    ⏳ users                 ⏳ roles
├─ ⏳ reports                ⏳ knowledge_articles    ⏳ audit_logs
├─ ⏳ compliance_checks      ⏳ predictions
└─ (未來擴充表格)

                                  │
                                  ▼ 外部通訊層
==============================================================
📁 外部通訊 / 資料源
├─ ✅ 串口讀取服務 (SerialReader) ── 接收模擬器/設備數據
├─ ⏳ MQTT 客戶端 (未來多設備支援)
└─ ⏳ 郵件服務 (異常通知/報告發送)

                                  │ (串口數據)
                                  ▼
==============================================================
📁 虛擬串口橋接器 (socat) - 提供可配對的虛擬串口 (如 /dev/ttysxxx)
==============================================================
                                  │
                                  ▼
📁 模擬器 / 真實設備層
├─ ✅ 慶聲溫箱模擬器 (KsonChamber) ── 溫度、濕度
├─ ⏳ 金頓振動機模擬器 (KingShaker) ── 頻率、加速度
├─ ⏳ 落下試驗機模擬器 (DropTester) ── 高度、次數
└─ ⏳ 其他設備 (鹽霧、IP防護等) ── 可擴充

                                  │
                                  ▼
📁 真實設備 (未來替換模擬器) - 透過串口伺服器連接 (如 MOXA NPort)
==============================================================
✅ 已完成 ｜ ⏳ 規劃中