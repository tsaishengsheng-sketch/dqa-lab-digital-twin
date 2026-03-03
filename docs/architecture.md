# 🏗️ DQA LAB 數位雙生平台 - 系統完整架構圖

本文件詳列所有已完成與規劃中之模組，作為後續開發追蹤使用。

---

## 📁 客戶端 (Browser) - React 前端模塊
本層級負責 UI 呈現與 SOP 流程引導。

* **✅ 全域路由控制 (App Router)**: 由 `App.jsx` 統一管理頂部導航列，確保頁面切換不產生重複 UI。
* **✅ 儀表板 (Dashboard)**: 即時趨勢圖、最新數值顯示。
* **✅ SOP 執行頁 (SOPPage)**: 
    * 採用 **40/60 雙欄佈局**：左側數據監控、右側操作面板。
    * 實作狀態脈衝動畫 (Pulse) 與響應式高度計算。
    * **✅ 動態 SOP 列表**: 從後端動態獲取測試程序，支援環境測試標準。
    * **✅ 移除硬編碼 standardMap**: `standard_id` 直接從後端 API 取得，前後端不再需要手動同步。
* **✅ 響應式佈局 (Responsive UI)**: 自動適應視窗縮放，確保控制按鈕與狀態欄不跑位。
* **✅ 狀態同步修正**: Dashboard 與 SOPPage 現在對 `RUNNING`、`FINISHING`、`PAUSED`、`EMERGENCY` 四種狀態都能正確顯示任務名稱。
* **⏳ 治具管理 (Fixtures)**: 治具清單、借用狀態追蹤。
* **⏳ 異常看板 (Issues)**: 數據偏差告警、設備 Error Code 紀錄。
* **⏳ Thermal 工作流 (Thermal)**: 熱測試專用自動化流程。
* **⏳ 報告檢視 (Reports)**: 測試結果總結、圖表導出。
* **⏳ 專案管理 (Projects)**: 實驗專案歸類、時程追蹤。
* **⏳ 設備管理 (Devices)**: 15 台溫箱狀態總覽 (LabVIEW 轉生目標)。
* **⏳ 知識庫 (Knowledge)**: 測試標準 (ISO/IEC)、設備操作手冊。
* **⏳ 使用者中心 (User)**: 權限控管、個人執行紀錄。

---

## 📁 後端 API 路由層 (FastAPI)
提供與前端、資料庫及硬體層通訊的 REST API。

* **✅ `/api/latest`**: 每秒輪詢之核心介面，獲取最新溫濕度與模擬器狀態。
* **✅ `/api/sop/`**: 動態獲取 SOP 列表（優先從環境測試標準讀取），回傳包含 `standard_id` 欄位。
* **✅ `/api/sop/start`**: 觸發指定 SOP 執行，進入物理模擬狀態。
* **✅ `/api/stop/emergency`**: 強制系統歸零，解除所有運行鎖定（緊急制動）。
* **✅ `/api/stop/pause`**: 暫停模擬並解鎖前端按鈕，允許臨時切換測試項目。
* **✅ `/api/stop/normal`**: 進入收尾狀態，引導溫度回歸安全室溫。
* **✅ 靜態日誌優化**: 實作 `--no-access-log` 機制，過濾重複輪詢，提升終端機開發讀取性。
* **✅ Router 註冊修正**: `include_router` 移至應用層級，修復路由可能無法正確註冊的問題。
* **⏳ `/api/fixtures`**: 治具 CRUD 介面。
* **⏳ `/api/reports`**: 自動化報告生成引擎。
* **⏳ `/api/auth`**: 登入驗證與 JWT 授權。
* **⏳ Pydantic 輸入驗證**: `/api/sop/start` 改用強型別 BaseModel 取代 `Dict[str, Any]`。

---

## 📁 環境測試標準模組 (Standards & Compliance)
支援國際電氣、電子與鐵路設備環境測試標準。

### **已整合標準** ✅
* **EN50155** - 歐洲鐵路設備環保測試
  * 高溫儲存: 70°C, 16 小時，升溫速率 ≤ 5°C/分鐘
  * 低溫儲存: -40°C, 16 小時，降溫速率 ≤ 5°C/分鐘

* **IEC 60068-2-14** - 溫度循環測試
  * 低溫: -40°C ↔ 高溫: 85°C, 5 個循環
  * 轉換速率: 2°C/分鐘，每溫度停留 1 小時

* **IEC 60068-2-30** - 濕熱循環測試
  * 溫度: 25°C ↔ 55°C，濕度: 95% RH
  * 6 個循環，每循環 24 小時

### **標準定義檔** (`standards.py`)
* **中央管理所有測試參數**: 升溫/降溫速率、停留時間、循環次數、濕度控制
* **SOP 步驟定義**: 每個標準包含完整的測試流程步驟
* **動態導出函數**: `get_ramp_rate()`, `get_all_standards()`, `get_sop_by_standard()`, `get_standard()`
* **目標溫度來源修正**: 物理模擬引擎改從 `standards.py` 直接讀取目標溫度，不再靠 SOP 名稱字串判斷。

### **規劃中的標準** ⏳
* **IEC61850** - 電力系統通訊標準環境測試
* **KEMA** - 歐洲能源認證標準
* **NEMA** - 美國電氣設備標準

---

## 📁 業務服務層 (Services) & 資料模型 (SQLite)
核心邏輯處理與持久化儲存。

### **業務邏輯 (Services)**
* **✅ 物理模擬引擎 (Simulator)**: 
  * 模擬物理升降溫斜率、目標值趨近演算法、狀態機轉移。
  * **✅ 標準化升降溫**: 根據環境測試標準動態限制升降溫速率。
  * **✅ 熱損失模型**: 模擬環境溫度的熱損失效應。
  * **✅ 隨機抖動**: 加入 ±0.15°C 的隨機變化，增加真實感。
  * **✅ 目標溫度修正**: 改從 `get_standard()` 讀取 `high_temperature` / `target_temperature`，移除脆弱的名稱字串判斷。
* **✅ 終端機日誌 (Console Monitor)**: 顯示模擬器當前任務細節。
* **✅ 即時數據快取 (AICM_CACHE)**: 確保串口與 API 數據交換零延遲。
* **⏳ 數據分析**: (預測/相似檢索)。
* **⏳ 稽核合規**: (ISO 17025 數據不可竄改紀錄)。

### **資料庫表格 (Models)**
* **✅ `device_data`**: 歷史數據紀錄。
* **✅ `sop_templates`**: SOP 步驟定義。
* **✅ `sop_executions`**: 執行歷程主表。
* **⏳ `test_validations`**: 測試是否符合標準的驗證紀錄。
* **⏳ `devices`**: 15 台設備身分與即時狀態 (IP, Code, ID)。
* **⏳ `users`**: 使用者權限管理。

---

## 📁 通訊與設備模擬層
底層硬體介接與環境模擬。

* **✅ 串口讀取服務 (SerialReader)**: 異步監聽串口數據流。
* **✅ 虛擬串口橋接器 (socat)**: 提供虛擬連線環境。
* **✅ 慶聲溫箱模擬器 (KsonChamber)**: 模擬真實設備回傳字串。

---

## 🔄 數據流程圖
```
環境測試標準 (standards.py)
        ↓
SOP 管理層 (sop.py)        ← 回傳 standard_id 給前端
        ↓
前端動態列表 (SOPPage.jsx) ← 直接使用 standard_id，不再查表
        ↓
使用者選擇 SOP
        ↓
啟動 SOP (/api/sop/start)
        ↓
物理模擬引擎 (main.py)     ← 從 get_standard() 讀取目標溫度
        ↓ (受標準速率限制)
溫度/濕度變化
        ↓
實時 API (/api/latest)
        ↓
前端圖表更新 (Dashboard.jsx / SOPPage.jsx) ← 四種狀態都正確顯示
```

---

## 📊 完成度統計

| 模組 | 狀態 | 說明 |
|------|------|------|
| 前端路由 | ✅ 完成 | App.jsx 統一管理 |
| 儀表板 | ✅ 完成 | 實時溫濕度顯示，四狀態同步修正 |
| SOP 執行 | ✅ 完成 | 動態列表 + 標準整合 + 移除硬編碼 |
| 環境測試標準 | ✅ 完成 | EN50155, IEC60068 |
| 物理模擬 | ✅ 完成 | 標準化升降溫，目標溫度從標準讀取 |
| 串口通訊 | ✅ 完成 | socat 虛擬環境 |
| 數據庫 | ✅ 完成 | SQLite + SQLAlchemy |
| Router 註冊 | ✅ 修正 | include_router 移至應用層級 |
| 認證系統 | ⏳ 規劃中 | JWT 認證 |
| 權限管理 | ⏳ 規劃中 | 用戶角色 |
| 報告生成 | ⏳ 規劃中 | CSV 導出 |
| 監控告警 | ⏳ 規劃中 | Prometheus |
| Pydantic 驗證 | ⏳ 規劃中 | /api/sop/start 強型別輸入 |

---

## 📝 修改紀錄

### 2026-03-03
- **fix**: `include_router` 移至應用層級，修復路由註冊問題 (`main.py`)
- **fix**: 目標溫度改從 `get_standard()` 讀取，移除靠名稱字串判斷的脆弱邏輯 (`main.py`)
- **fix**: Dashboard 修正 `FINISHING`/`PAUSED`/`EMERGENCY` 狀態下任務名稱不顯示的問題 (`Dashboard.jsx`)
- **feat**: `SopResponse` 新增 `standard_id` 欄位，後端直接回傳給前端 (`sop.py`)
- **fix**: 移除前端硬編碼 `standardMap`，改用後端回傳的 `standard_id` (`SOPPage.jsx`)