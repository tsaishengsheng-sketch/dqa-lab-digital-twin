# 🏗️ DQA LAB 數位雙生平台 - 系統完整架構圖

本文件詳列所有已完成與規劃中之模組，作為後續開發追蹤使用。

---

## 📁 客戶端 (Browser) - React 前端模塊

* **✅ 全域路由控制 (App Router)**: 由 `App.jsx` 統一管理頂部導航列。
* **✅ 儀表板 (Dashboard)**: 即時趨勢圖、最新數值顯示。
* **✅ SOP 執行頁 (SOPPage)**:
    * 採用 **40/60 雙欄佈局**：左側數據監控、右側操作面板。
    * **✅ 狀態自動切換**: 待機顯示注意事項 + SOP 列表；執行中顯示步驟清單，兩種畫面自動切換。
    * **✅ 暫停切換邏輯修正**: `RUNNING ↔ PAUSED` 真正來回切換。
    * **✅ 停止後回待機**: 正常停止 / 緊急停止後前端正確切回待機畫面。
    * **✅ SOP 步驟追蹤**: 啟動後顯示 4 步驟清單，Step 1、2 自動勾選，Step 3、4 人工確認。
    * **✅ 動態 SOP 列表**: 從後端動態獲取，`standard_id` 直接使用不需查表。
    * **✅ 上架安全確認**: 四項注意事項全勾才能啟動測試。
* **⏳ 治具管理 (Fixtures)**: 治具清單、借用狀態追蹤。
* **⏳ 異常看板 (Issues)**: 數據偏差告警、設備 Error Code 紀錄。
* **⏳ 報告檢視 (Reports)**: 測試結果總結、CSV 導出。
* **⏳ 設備管理 (Devices)**: 15 台溫箱狀態總覽。
* **⏳ 使用者中心 (User)**: 權限控管、個人執行紀錄。

---

## 📁 後端 API 路由層 (FastAPI)

* **✅ `/api/latest`**: 每秒輪詢，獲取最新溫濕度與狀態，含完整描述文字。
* **✅ `/api/sop/`**: 動態獲取 SOP 列表，回傳含 `standard_id` 欄位。
* **✅ `/api/sop/start`**: 觸發指定 SOP，Pydantic `StartSopRequest` 強型別驗證。
* **✅ `/api/sop-executions/`**: 儲存 SOP 執行紀錄（步驟完成狀態）到資料庫。
* **✅ `/api/sop-executions/{id}`**: 讀取指定執行紀錄。
* **✅ `/api/stop/pause`**: `RUNNING ↔ PAUSED` 真正切換。
* **✅ `/api/stop/normal`**: 進入 `FINISHING`，降溫完成後自動回 `IDLE`。
* **✅ `/api/stop/emergency`**: 強制進入 `EMERGENCY` 狀態。
* **⏳ `/api/reports`**: CSV 報告生成引擎。
* **⏳ `/api/auth`**: JWT 登入驗證。

---

## 📁 環境測試標準模組 (standards.py)

### 已整合標準 ✅
* **EN50155** — 高溫儲存 70°C / 低溫儲存 -40°C，速率 ≤ 5°C/min
* **IEC 60068-2-14** — 溫度循環 -40°C ↔ 85°C，速率 2°C/min，5 循環
* **IEC 60068-2-30** — 濕熱循環 25°C ↔ 55°C，95% RH，6 循環

### SOP 步驟統一格式
所有標準統一為 4 步驟：
1. 設備開機與檢查（啟動時自動勾選）
2. 確認測試參數（啟動時自動勾選）
3. 監控測試過程（人工確認）
4. 儲存測試紀錄（人工確認）

### 規劃中 ⏳
* IEC61850、KEMA、NEMA

---

## 📁 業務服務層 & 資料模型

### 物理模擬引擎 ✅
* 升降溫斜率模擬，遵守標準速率限制
* `FINISHING` 狀態降溫完成後自動切回 `IDLE`
* `EMERGENCY` 狀態溫度微幅抖動（不主動降溫）
* ±0.1°C 隨機抖動增加真實感

### 資料庫表格
* **✅ `device_data`**: 歷史溫濕度紀錄
* **✅ `sop_executions`**: 執行歷程主表
* **✅ `step_records`**: 每步驟完成狀態
* **⏳ `devices`**: 15 台設備身分與狀態
* **⏳ `users`**: 使用者權限管理

---

## 🔄 數據流程圖

```
環境測試標準 (standards.py)
        ↓
SOP 管理層 (sop.py)              ← 回傳 standard_id 給前端
        ↓
前端待機畫面 (SOPPage.jsx)       ← 四項注意事項全勾才解鎖
        ↓
使用者選擇 SOP 並啟動
        ↓
Pydantic 驗證 (StartSopRequest)  ← 強型別，錯誤立即 422
        ↓
物理模擬引擎 (main.py)           ← 從 get_standard() 讀取目標溫度
        ↓
前端切換執行畫面                 ← Step 1、2 自動勾選
        ↓
使用者監控並勾選 Step 3、4
        ↓
正常停止 → FINISHING → 自動降溫 → IDLE → 回待機畫面
```

---

## 📊 完成度統計

| 模組 | 狀態 | 說明 |
|------|------|------|
| 前端路由 | ✅ | App.jsx 統一管理 |
| 儀表板 | ✅ | 實時溫濕度顯示 |
| SOP 執行畫面切換 | ✅ | 待機/執行中自動切換 |
| SOP 步驟追蹤 | ✅ | 4 步驟，啟動自動勾選前兩步 |
| 上架安全確認 | ✅ | 四項全勾才能啟動 |
| 暫停切換邏輯 | ✅ | RUNNING ↔ PAUSED 真正切換 |
| 停止後回待機 | ✅ | FINISHING 自動回 IDLE |
| 環境測試標準 | ✅ | EN50155, IEC60068 |
| 物理模擬 | ✅ | 標準化升降溫 |
| 執行紀錄 API | ✅ | sop_execution router 已註冊 |
| Pydantic 驗證 | ✅ | StartSopRequest |
| 測試報告 CSV | ⏳ | 規劃中 |
| 認證系統 | ⏳ | JWT |
| 設備管理 | ⏳ | 15 台溫箱 |

---

## 📝 修改紀錄

### 2026-03-03
- **fix**: `include_router` 移至應用層級，修復重複 import (`main.py`)
- **fix**: 目標溫度改從 `get_standard()` 讀取 (`main.py`)
- **fix**: `FINISHING` 降溫完成後自動回 `IDLE` (`main.py`)
- **fix**: 暫停切換改為 `RUNNING ↔ PAUSED` 真正切換 (`main.py`)
- **fix**: Dashboard 四種狀態正確顯示任務名稱 (`Dashboard.jsx`)
- **feat**: `SopResponse` 新增 `standard_id` 欄位 (`sop.py`)
- **feat**: Pydantic `StartSopRequest` 輸入驗證 (`sop.py`)
- **feat**: 註冊 `sop_execution` router (`main.py`)
- **feat**: 上架驗證注意事項確認框 (`SOPPage.jsx`)
- **feat**: 待機/執行中畫面自動切換 (`SOPPage.jsx`)
- **feat**: SOP 步驟清單，啟動自動勾選 Step 1、2 (`SOPPage.jsx`)
- **refactor**: `standards.py` 統一步驟為 4 步，移除「啟動測試」

### 2026-03-02
- 整合 EN50155、IEC60068 環境測試標準
- 動態 SOP 管理系統
- 前端 SOP 列表動態載入