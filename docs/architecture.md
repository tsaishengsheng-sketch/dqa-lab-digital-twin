# 🏗️ DQA LAB 數位雙生平台 - 系統完整架構圖

本文件詳列所有已完成與規劃中之模組，作為後續開發追蹤使用。

---

## 📁 客戶端 (Browser) - React 前端模塊

* **✅ 全域路由控制 (App Router)**: 由 `App.jsx` 統一管理頂部導航列。
* **✅ 儀表板 (Dashboard)**: 即時趨勢圖、最新數值顯示，統一使用 axios，支援 RUNNING/PAUSED/FINISHING/EMERGENCY/IDLE/OFFLINE 六種狀態顏色。
* **✅ SOP 執行頁 (SOPPage)**:
    * 採用 **40/60 雙欄佈局**：左側數據監控、右側操作面板。
    * **✅ 三步驟法規選擇 UI**：法規 → 版本/Class → 測試條件，從 `/api/sop/standards/tree` 動態載入，選定後顯示完整測試條件說明。
    * **✅ 狀態自動切換**: 待機顯示注意事項 + SOP 列表；執行中顯示步驟清單，兩種畫面自動切換。
    * **✅ 暫停切換邏輯**: `RUNNING ↔ PAUSED` 真正來回切換。
    * **✅ 停止後回待機**: 正常停止 / 緊急停止後前端正確切回待機畫面。
    * **✅ SOP 步驟追蹤**: 依各標準客制化步驟數，Step 1、2 自動勾選，其餘人工確認。
    * **✅ 儲存 + 下載**: 全步驟完成後可儲存執行紀錄，儲存後顯示「下載 CSV 測試報告」按鈕。
    * **✅ 上架安全確認**: 四項注意事項全勾才能啟動測試。
* **✅ 報告檢視頁 (ReportsPage)**:
    * 歷史執行紀錄列表，顯示 SOP ID、執行時間、PASS/FAIL 狀態徽章、步驟完成率進度條。
    * 搜尋（SOP ID / 編號）+ ALL / PASS / FAIL 快速篩選。
    * 統計卡列：執行總數、PASS 數、FAIL 數、通過率。
    * 左右雙欄：左側列表 + 右側詳情（步驟記錄、測試參數、溫濕度統計）。
    * ISO 17025 CSV 報告下載，自動從 `content-disposition` 取得正確檔名。
* **⏳ 治具管理 (Fixtures)**: 治具清單、借用狀態追蹤。
* **⏳ 異常看板 (Issues)**: 數據偏差告警、設備 Error Code 紀錄。
* **⏳ 設備管理 (Devices)**: 15 台溫箱狀態總覽。
* **⏳ 使用者中心 (User)**: 權限控管、個人執行紀錄。

---

## 📁 後端 API 路由層 (FastAPI)

### 已完成 ✅

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET  | `/api/latest` | 即時溫濕度與狀態（每秒輪詢） |
| GET  | `/api/sop/` | SOP 列表（從 STANDARD_TREE 自動展開） |
| GET  | `/api/sop/standards/tree` | 完整三層標準樹（法規→版本→測試條件），供前端 UI 使用 |
| POST | `/api/sop/start` | 啟動 SOP，更新 AICM_CACHE 狀態 |
| POST | `/api/sop-executions/` | 儲存 SOP 執行紀錄（含步驟完成狀態） |
| GET  | `/api/sop-executions/{id}` | 讀取指定執行紀錄 |
| GET  | `/api/reports/csv/{execution_id}` | 下載 ISO 17025 格式 CSV 測試報告（big5 編碼，Excel 相容） |
| GET  | `/api/reports/list` | 所有執行紀錄列表 |
| POST | `/api/stop/pause` | `RUNNING ↔ PAUSED` 切換 |
| POST | `/api/stop/normal` | 進入 `FINISHING`，降溫完成後自動回 `IDLE` |
| POST | `/api/stop/emergency` | 強制進入 `EMERGENCY` 狀態 |

### 規劃中 ⏳
* **`/api/auth`** — JWT 登入驗證
* **`/api/devices`** — 15 台溫箱管理（動態 device_id）
* **`/api/errors`** — 故障記錄查詢

---

## 📁 環境測試標準模組 (standards.py)

### 架構：三層巢狀 `STANDARD_TREE`

```
STANDARD_TREE
├── 法規（IEC 60068 / EN 50155 / IEC 61850-3 / DNV / KEMA / NMEA）
│   ├── 版本（Ed.1 / Ed.2 / 2007 / 2017 / CG-0339 / Std.Cert.2.4 …）
│   │   └── 測試條件（乾熱 / 冷測 / 濕熱 / 溫度循環 / 熱衝擊 …）
│   │       ├── 溫度範圍、速率、停留時間、循環次數
│   │       ├── 濕度設定、通電/非通電
│   │       ├── 溫度容差、濕度容差（各標準不同）
│   │       ├── 法規條文參考（IEC/EN 條款編號）
│   │       └── 客制化 SOP 步驟（依測試類型自動生成）
```

`STANDARDS_AND_SOPS` 由 `_build_flat_standards()` 從 `STANDARD_TREE` 自動展開，供 `sop.py`、`main.py`、`reports.py` 向後相容使用。

### 已整合標準（共 62 個測試條件）✅

| 法規 | 版本數 | 測試條件數 | 主要測試項目 |
|------|--------|-----------|------------|
| **IEC 60068** | 4 | 12 | Test Ab/Ad（冷）、Ba/Bb（乾熱）、Na/Nb（溫度循環/熱衝擊）、Db（濕熱循環） |
| **EN 50155** | 2 | 18 | OT1~OT6 各高溫/低溫分開、ST1 開機延伸、快速溫度變化（隧道模擬）、濕熱循環 |
| **IEC 61850-3** | 2 | 9 | Class C1/C2/C3 各自乾熱 + 冷測 + 濕熱、Ed.1 向後相容 |
| **DNV** | 2 | 12 | CG-0339 Class A/B/C/D、Std.Cert.2.4 舊版、C/D 冷測強制標註 |
| **KEMA** | 1 | 4 | 乾熱（Test Bb）、冷測（Test Ab）、濕熱穩態（Test Cab）、溫度循環（Test Nb） |
| **NMEA** | 2 | 7 | IEC 60945 受保護/暴露裝置分開、NMEA 0183/2000 各自乾熱+冷測+濕熱 |

### 容差規格（依法規不同）

| 法規 | 溫度容差 | 濕度容差 | 依據 |
|------|--------|---------|------|
| IEC 60068 / EN 50155 / IEC 61850-3 / KEMA / NMEA | ±2°C | ±5%RH | IEC 60068 一般量測 |
| DNV CG-0339 / DNV Std.Cert.2.4 | ±2°C | **±10%RH** | DNVGL-CG-0339 規定 |

### SOP 步驟工廠
* **`_steps_single_temp()`** — 單一溫度測試（乾熱/冷測）：5 步驟，含開機預檢、參數設定（含 schema）、啟動監控、完成確認、儲存紀錄
* **`_steps_cycle()`** — 循環測試（溫度循環/濕熱循環）：6 步驟，含中期檢查（optional）

---

## 📁 業務服務層 & 資料模型

### 物理模擬引擎 (main.py) ✅
* 升降溫斜率模擬，遵守各標準速率限制（從 `get_ramp_rate()` 動態讀取）
* **每 10 秒寫一次資料庫**（原每秒，優化後減少 90% 寫入量）
* **自動清理 7 天前舊數據**（每次寫入後執行 `_cleanup_old_data()`）
* `FINISHING` 狀態自動降溫至 25°C 後回 `IDLE`
* `EMERGENCY` 狀態微幅抖動（不主動降溫）
* ±0.1°C 隨機抖動增加真實感

### 測試報告引擎 (reports.py) ✅
* 符合 **ISO/IEC 17025:2017** 格式，共 7 節
* 報告節次：識別資訊 → 樣品資訊 → 測試條件 → 步驟記錄 → 統計摘要 → **PASS/FAIL 自動判定** → 原始數據
* 容差判定從各標準 `temp_tolerance` / `humi_tolerance` 讀取（非寫死）
* **big5 編碼**，macOS / Windows Excel 中文正確顯示
* 溫度數值 `round(value, 2)` 防止浮點數精度問題
* 報告命名：`RPT-YYYYMMDD-{id:03d}_{sop_id}.csv`

### 報告兩層架構

```
測試完成
    │
    ├─ 內部紀錄（系統自動）
    │       GET /api/reports/csv/{id}
    │       ISO 17025 CSV，含原始溫濕度數據
    │       → 工程師自存 / ReportsPage 查閱
    │
    └─ 對外 QA Test Report（工程師人工整理）
            docs/templates/QA_Test_Report_Template.docx
            填入關鍵數據 + 照片 + 主管簽名
            → 發給客戶 / 認證機構
```

> 模板同時存放於 `backend/templates/` 供未來後端半自動填入功能使用。

### 資料庫表格 (SQLite)

| 表格 | 狀態 | 說明 |
|------|------|------|
| `device_data` | ✅ | 歷史溫濕度（每 10 秒，保留 7 天） |
| `sop_executions` | ✅ | 執行歷程主表 |
| `step_records` | ✅ | 每步驟完成狀態 |
| `sop_templates` | ✅ | 自訂 SOP（DB 版，補充 standards.py） |
| `devices` | ⏳ | 15 台設備身分與狀態 |
| `users` | ⏳ | 使用者權限管理 |
| `error_logs` | ⏳ | 故障記錄（緊急停止事件） |

---

## 📁 通訊與設備模擬層

* **✅ 虛擬串口橋接器 (socat)**: 提供虛擬連線環境（macOS/Linux）
* **✅ 慶聲溫箱模擬器 (KsonChamber)**: 模擬 KSON AICM 真實設備回傳字串
* **⏳ RS-485/RJ45 真實串口通訊**: 對接真實 KSON 溫箱（Phase 3）

---

## 🔄 數據流程圖

```
STANDARD_TREE (standards.py)
        │
        ├─ GET /api/sop/standards/tree
        │       └─ 前端三步驟選擇 UI
        │              法規 → 版本/Class → 測試條件
        │
        └─ STANDARDS_AND_SOPS（自動展開）
                │
                ├─ sop.py       ← GET /api/sop/
                ├─ main.py      ← get_ramp_rate() 限制速率
                └─ reports.py   ← 讀取容差做 PASS/FAIL 判定
                        │
                使用者確認注意事項 → POST /api/sop/start
                        │
                物理模擬引擎（每 10 秒寫 device_data）
                        │
                前端輪詢 /api/latest（每秒）
                        │
                步驟逐一人工勾選完成
                        │
                POST /api/sop-executions/（儲存紀錄）
                        │
                GET /api/reports/csv/{id}（下載 ISO 17025 報告）
                        │
                ReportsPage 查閱歷史紀錄 / 再次下載
                        │
        正常停止 → FINISHING → 自動降溫 → IDLE → 回待機畫面
```

---

## 📊 完成度統計

| 模組 | 狀態 | 說明 |
|------|------|------|
| 前端路由 | ✅ | App.jsx 統一管理 |
| 儀表板 | ✅ | 六種狀態顏色，統一 axios |
| SOP 三步驟法規選擇 | ✅ | 法規→版本→測試條件，動態載入 |
| SOP 執行畫面切換 | ✅ | 待機/執行中自動切換 |
| SOP 步驟追蹤 | ✅ | 客制化步驟，啟動自動勾選前兩步 |
| 上架安全確認 | ✅ | 四項全勾才能啟動 |
| 暫停/停止邏輯 | ✅ | RUNNING↔PAUSED，FINISHING→IDLE |
| 環境測試標準 | ✅ | 6 法規，62 個測試條件，官方參數 |
| 物理模擬引擎 | ✅ | 標準化升降溫，每 10 秒寫 DB |
| DB 自動清理 | ✅ | 保留最近 7 天數據 |
| 執行紀錄 API | ✅ | sop_execution router |
| CSV 測試報告 | ✅ | ISO 17025 格式，PASS/FAIL 判定 |
| 報告下載按鈕 | ✅ | 儲存後顯示，big5 Excel 相容 |
| 報告檢視頁 | ✅ | ReportsPage，篩選/搜尋/詳情/下載 |
| 對外報告模板 | ✅ | QA_Test_Report_Template.docx，兩層架構 |
| 多台設備架構 | ⏳ | 動態 device_id，15 台溫箱 |
| 故障記錄與通報 | ⏳ | error_logs 表，Email 通報 |
| 認證系統 | ⏳ | JWT |
| RS-485 真實通訊 | ⏳ | Phase 3 |

---

## 📝 修改紀錄

### 2026-03-04
- **feat**: `ReportsPage.jsx` 報告檢視頁，統計卡列、搜尋篩選、左右雙欄詳情、CSV 下載
- **feat**: 新增 `docs/templates/QA_Test_Report_Template.docx` — 對外 QA 測試報告模板（8 章節，封面/目錄/簽名欄，已移除商標）
- **feat**: 新增 `backend/templates/QA_Test_Report_Template.docx` — 供未來後端半自動填入使用
- **feat**: `standards.py` 重構為三層巢狀 `STANDARD_TREE`，新增 IEC 60068 完整系列（Test Ab/Ad/Ba/Bb/Na/Nb/Db）
- **feat**: EN 50155:2017 新增 OT1~OT6 各高溫/低溫分開、ST1 開機延伸溫度、快速溫度變化測試
- **feat**: IEC 61850-3 Ed.2 新增 Class C1/C2/C3 分別測試條件；保留 Ed.1 向後相容
- **feat**: DNV 新增 DNVGL-CG-0339:2019 Class A/B/C/D（含穩態/循環濕熱區分）；保留舊版 Std.Cert.2.4
- **feat**: KEMA 新增乾熱/冷測/濕熱穩態/溫度循環四項測試
- **feat**: NMEA 細分受保護/暴露裝置，NMEA 0183/2000 獨立版本
- **feat**: `STANDARDS_AND_SOPS` 改由 `_build_flat_standards()` 自動展開（向後相容）
- **feat**: `GET /api/sop/standards/tree` 新端點，回傳完整三層結構供前端使用
- **feat**: `sop.py` 更新配合新 `STANDARDS_AND_SOPS` 展開方式
- **perf**: `device_data` 寫入頻率從每秒改為每 10 秒，減少 90% 寫入量
- **feat**: `_cleanup_old_data()` 自動清理 7 天前舊數據
- **feat**: CSV 報告下載按鈕（儲存紀錄後顯示）
- **fix**: CSV 報告編碼改為 big5，解決 macOS Excel 中文亂碼
- **fix**: CSV 報告溫度數值 `round(value, 2)` 防止浮點精度問題
- **feat**: 報告容差從各標準 `temp_tolerance`/`humi_tolerance` 讀取（非寫死 ±2°C）

### 2026-03-03
- **fix**: `include_router` 移至應用層級，修復重複 import（`main.py`）
- **fix**: 物理模擬目標溫度改從 `get_standard()` 讀取（`main.py`）
- **fix**: Dashboard 六種狀態正確顯示任務名稱（`Dashboard.jsx`）
- **fix**: `FINISHING` 降溫完成後自動回 `IDLE`（`main.py`）
- **fix**: 暫停切換改為 `RUNNING ↔ PAUSED` 真正切換（`main.py`）
- **feat**: `SopResponse` 新增 `standard_id` 欄位（`sop.py`）
- **feat**: Pydantic `StartSopRequest` 輸入驗證（`sop.py`）
- **feat**: 上架驗證注意事項確認框（`SOPPage.jsx`）
- **feat**: 待機/執行中畫面自動切換邏輯（`SOPPage.jsx`）
- **feat**: SOP 步驟清單，啟動後自動勾選 Step 1、2（`SOPPage.jsx`）
- **feat**: 註冊 `sop_execution` router，支援執行紀錄 API（`main.py`）
- **feat**: ISO 17025 格式測試報告（`reports.py`）
- **refactor**: `standards.py` 統一步驟為 4 步，移除「啟動測試」步驟
- **refactor**: `init_db()` 合併進 `models.py`，`database.py` 改為轉發層
- **fix**: `datetime.utcnow` 改為 `datetime.now(timezone.utc)`（Python 3.12 相容）

### 2026-03-02
- 整合 EN50155、IEC60068 環境測試標準
- 動態 SOP 管理系統
- 前端 SOP 列表動態載入# 🏗️ DQA LAB 數位雙生平台 - 系統完整架構圖

本文件詳列所有已完成與規劃中之模組，作為後續開發追蹤使用。

---

## 📁 客戶端 (Browser) - React 前端模塊

* **✅ 全域路由控制 (App Router)**: 由 `App.jsx` 統一管理頂部導航列。
* **✅ 儀表板 (Dashboard)**: 即時趨勢圖、最新數值顯示，統一使用 axios，支援 RUNNING/PAUSED/FINISHING/EMERGENCY/IDLE/OFFLINE 六種狀態顏色。
* **✅ SOP 執行頁 (SOPPage)**:
    * 採用 **40/60 雙欄佈局**：左側數據監控、右側操作面板。
    * **✅ 三步驟法規選擇 UI**：法規 → 版本/Class → 測試條件，從 `/api/sop/standards/tree` 動態載入，選定後顯示完整測試條件說明。
    * **✅ 狀態自動切換**: 待機顯示注意事項 + SOP 列表；執行中顯示步驟清單，兩種畫面自動切換。
    * **✅ 暫停切換邏輯**: `RUNNING ↔ PAUSED` 真正來回切換。
    * **✅ 停止後回待機**: 正常停止 / 緊急停止後前端正確切回待機畫面。
    * **✅ SOP 步驟追蹤**: 依各標準客制化步驟數，Step 1、2 自動勾選，其餘人工確認。
    * **✅ 儲存 + 下載**: 全步驟完成後可儲存執行紀錄，儲存後顯示「下載 CSV 測試報告」按鈕。
    * **✅ 上架安全確認**: 四項注意事項全勾才能啟動測試。
* **✅ 報告檢視頁 (ReportsPage)**:
    * 歷史執行紀錄列表，顯示 SOP ID、執行時間、PASS/FAIL 狀態徽章、步驟完成率進度條。
    * 搜尋（SOP ID / 編號）+ ALL / PASS / FAIL 快速篩選。
    * 統計卡列：執行總數、PASS 數、FAIL 數、通過率。
    * 左右雙欄：左側列表 + 右側詳情（步驟記錄、測試參數、溫濕度統計）。
    * ISO 17025 CSV 報告下載，自動從 `content-disposition` 取得正確檔名。
* **⏳ 治具管理 (Fixtures)**: 治具清單、借用狀態追蹤。
* **⏳ 異常看板 (Issues)**: 數據偏差告警、設備 Error Code 紀錄。
* **⏳ 設備管理 (Devices)**: 15 台溫箱狀態總覽。
* **⏳ 使用者中心 (User)**: 權限控管、個人執行紀錄。

---

## 📁 後端 API 路由層 (FastAPI)

### 已完成 ✅

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET  | `/api/latest` | 即時溫濕度與狀態（每秒輪詢） |
| GET  | `/api/sop/` | SOP 列表（從 STANDARD_TREE 自動展開） |
| GET  | `/api/sop/standards/tree` | 完整三層標準樹（法規→版本→測試條件），供前端 UI 使用 |
| POST | `/api/sop/start` | 啟動 SOP，更新 AICM_CACHE 狀態 |
| POST | `/api/sop-executions/` | 儲存 SOP 執行紀錄（含步驟完成狀態） |
| GET  | `/api/sop-executions/{id}` | 讀取指定執行紀錄 |
| GET  | `/api/reports/csv/{execution_id}` | 下載 ISO 17025 格式 CSV 測試報告（big5 編碼，Excel 相容） |
| GET  | `/api/reports/list` | 所有執行紀錄列表 |
| POST | `/api/stop/pause` | `RUNNING ↔ PAUSED` 切換 |
| POST | `/api/stop/normal` | 進入 `FINISHING`，降溫完成後自動回 `IDLE` |
| POST | `/api/stop/emergency` | 強制進入 `EMERGENCY` 狀態 |

### 規劃中 ⏳
* **`/api/auth`** — JWT 登入驗證
* **`/api/devices`** — 15 台溫箱管理（動態 device_id）
* **`/api/errors`** — 故障記錄查詢

---

## 📁 環境測試標準模組 (standards.py)

### 架構：三層巢狀 `STANDARD_TREE`

```
STANDARD_TREE
├── 法規（IEC 60068 / EN 50155 / IEC 61850-3 / DNV / KEMA / NMEA）
│   ├── 版本（Ed.1 / Ed.2 / 2007 / 2017 / CG-0339 / Std.Cert.2.4 …）
│   │   └── 測試條件（乾熱 / 冷測 / 濕熱 / 溫度循環 / 熱衝擊 …）
│   │       ├── 溫度範圍、速率、停留時間、循環次數
│   │       ├── 濕度設定、通電/非通電
│   │       ├── 溫度容差、濕度容差（各標準不同）
│   │       ├── 法規條文參考（IEC/EN 條款編號）
│   │       └── 客制化 SOP 步驟（依測試類型自動生成）
```

`STANDARDS_AND_SOPS` 由 `_build_flat_standards()` 從 `STANDARD_TREE` 自動展開，供 `sop.py`、`main.py`、`reports.py` 向後相容使用。

### 已整合標準（共 62 個測試條件）✅

| 法規 | 版本數 | 測試條件數 | 主要測試項目 |
|------|--------|-----------|------------|
| **IEC 60068** | 4 | 12 | Test Ab/Ad（冷）、Ba/Bb（乾熱）、Na/Nb（溫度循環/熱衝擊）、Db（濕熱循環） |
| **EN 50155** | 2 | 18 | OT1~OT6 各高溫/低溫分開、ST1 開機延伸、快速溫度變化（隧道模擬）、濕熱循環 |
| **IEC 61850-3** | 2 | 9 | Class C1/C2/C3 各自乾熱 + 冷測 + 濕熱、Ed.1 向後相容 |
| **DNV** | 2 | 12 | CG-0339 Class A/B/C/D、Std.Cert.2.4 舊版、C/D 冷測強制標註 |
| **KEMA** | 1 | 4 | 乾熱（Test Bb）、冷測（Test Ab）、濕熱穩態（Test Cab）、溫度循環（Test Nb） |
| **NMEA** | 2 | 7 | IEC 60945 受保護/暴露裝置分開、NMEA 0183/2000 各自乾熱+冷測+濕熱 |

### 容差規格（依法規不同）

| 法規 | 溫度容差 | 濕度容差 | 依據 |
|------|--------|---------|------|
| IEC 60068 / EN 50155 / IEC 61850-3 / KEMA / NMEA | ±2°C | ±5%RH | IEC 60068 一般量測 |
| DNV CG-0339 / DNV Std.Cert.2.4 | ±2°C | **±10%RH** | DNVGL-CG-0339 規定 |

### SOP 步驟工廠
* **`_steps_single_temp()`** — 單一溫度測試（乾熱/冷測）：5 步驟，含開機預檢、參數設定（含 schema）、啟動監控、完成確認、儲存紀錄
* **`_steps_cycle()`** — 循環測試（溫度循環/濕熱循環）：6 步驟，含中期檢查（optional）

---

## 📁 業務服務層 & 資料模型

### 物理模擬引擎 (main.py) ✅
* 升降溫斜率模擬，遵守各標準速率限制（從 `get_ramp_rate()` 動態讀取）
* **每 10 秒寫一次資料庫**（原每秒，優化後減少 90% 寫入量）
* **自動清理 7 天前舊數據**（每次寫入後執行 `_cleanup_old_data()`）
* `FINISHING` 狀態自動降溫至 25°C 後回 `IDLE`
* `EMERGENCY` 狀態微幅抖動（不主動降溫）
* ±0.1°C 隨機抖動增加真實感

### 測試報告引擎 (reports.py) ✅
* 符合 **ISO/IEC 17025:2017** 格式，共 7 節
* 報告節次：識別資訊 → 樣品資訊 → 測試條件 → 步驟記錄 → 統計摘要 → **PASS/FAIL 自動判定** → 原始數據
* 容差判定從各標準 `temp_tolerance` / `humi_tolerance` 讀取（非寫死）
* **big5 編碼**，macOS / Windows Excel 中文正確顯示
* 溫度數值 `round(value, 2)` 防止浮點數精度問題
* 報告命名：`RPT-YYYYMMDD-{id:03d}_{sop_id}.csv`

### 報告兩層架構

```
測試完成
    │
    ├─ 內部紀錄（系統自動）
    │       GET /api/reports/csv/{id}
    │       ISO 17025 CSV，含原始溫濕度數據
    │       → 工程師自存 / ReportsPage 查閱
    │
    └─ 對外 QA Test Report（工程師人工整理）
            docs/templates/QA_Test_Report_Template.docx
            填入關鍵數據 + 照片 + 主管簽名
            → 發給客戶 / 認證機構
```

> 模板同時存放於 `backend/templates/` 供未來後端半自動填入功能使用。

### 資料庫表格 (SQLite)

| 表格 | 狀態 | 說明 |
|------|------|------|
| `device_data` | ✅ | 歷史溫濕度（每 10 秒，保留 7 天） |
| `sop_executions` | ✅ | 執行歷程主表 |
| `step_records` | ✅ | 每步驟完成狀態 |
| `sop_templates` | ✅ | 自訂 SOP（DB 版，補充 standards.py） |
| `devices` | ⏳ | 15 台設備身分與狀態 |
| `users` | ⏳ | 使用者權限管理 |
| `error_logs` | ⏳ | 故障記錄（緊急停止事件） |

---

## 📁 通訊與設備模擬層

* **✅ 虛擬串口橋接器 (socat)**: 提供虛擬連線環境（macOS/Linux）
* **✅ 慶聲溫箱模擬器 (KsonChamber)**: 模擬 KSON AICM 真實設備回傳字串
* **⏳ RS-485/RJ45 真實串口通訊**: 對接真實 KSON 溫箱（Phase 3）

---

## 🔄 數據流程圖

```
STANDARD_TREE (standards.py)
        │
        ├─ GET /api/sop/standards/tree
        │       └─ 前端三步驟選擇 UI
        │              法規 → 版本/Class → 測試條件
        │
        └─ STANDARDS_AND_SOPS（自動展開）
                │
                ├─ sop.py       ← GET /api/sop/
                ├─ main.py      ← get_ramp_rate() 限制速率
                └─ reports.py   ← 讀取容差做 PASS/FAIL 判定
                        │
                使用者確認注意事項 → POST /api/sop/start
                        │
                物理模擬引擎（每 10 秒寫 device_data）
                        │
                前端輪詢 /api/latest（每秒）
                        │
                步驟逐一人工勾選完成
                        │
                POST /api/sop-executions/（儲存紀錄）
                        │
                GET /api/reports/csv/{id}（下載 ISO 17025 報告）
                        │
                ReportsPage 查閱歷史紀錄 / 再次下載
                        │
        正常停止 → FINISHING → 自動降溫 → IDLE → 回待機畫面
```

---

## 📊 完成度統計

| 模組 | 狀態 | 說明 |
|------|------|------|
| 前端路由 | ✅ | App.jsx 統一管理 |
| 儀表板 | ✅ | 六種狀態顏色，統一 axios |
| SOP 三步驟法規選擇 | ✅ | 法規→版本→測試條件，動態載入 |
| SOP 執行畫面切換 | ✅ | 待機/執行中自動切換 |
| SOP 步驟追蹤 | ✅ | 客制化步驟，啟動自動勾選前兩步 |
| 上架安全確認 | ✅ | 四項全勾才能啟動 |
| 暫停/停止邏輯 | ✅ | RUNNING↔PAUSED，FINISHING→IDLE |
| 環境測試標準 | ✅ | 6 法規，62 個測試條件，官方參數 |
| 物理模擬引擎 | ✅ | 標準化升降溫，每 10 秒寫 DB |
| DB 自動清理 | ✅ | 保留最近 7 天數據 |
| 執行紀錄 API | ✅ | sop_execution router |
| CSV 測試報告 | ✅ | ISO 17025 格式，PASS/FAIL 判定 |
| 報告下載按鈕 | ✅ | 儲存後顯示，big5 Excel 相容 |
| 報告檢視頁 | ✅ | ReportsPage，篩選/搜尋/詳情/下載 |
| 對外報告模板 | ✅ | QA_Test_Report_Template.docx，兩層架構 |
| 多台設備架構 | ⏳ | 動態 device_id，15 台溫箱 |
| 故障記錄與通報 | ⏳ | error_logs 表，Email 通報 |
| 認證系統 | ⏳ | JWT |
| RS-485 真實通訊 | ⏳ | Phase 3 |

---

## 📝 修改紀錄

### 2026-03-04
- **feat**: `ReportsPage.jsx` 報告檢視頁，統計卡列、搜尋篩選、左右雙欄詳情、CSV 下載
- **feat**: 新增 `docs/templates/QA_Test_Report_Template.docx` — 對外 QA 測試報告模板
- **feat**: 新增 `backend/templates/QA_Test_Report_Template.docx` — 供未來後端半自動填入使用
- **feat**: `standards.py` 重構為三層巢狀 `STANDARD_TREE`，新增 IEC 60068 完整系列（Test Ab/Ad/Ba/Bb/Na/Nb/Db）
- **feat**: EN 50155:2017 新增 OT1~OT6 各高溫/低溫分開、ST1 開機延伸溫度、快速溫度變化測試
- **feat**: IEC 61850-3 Ed.2 新增 Class C1/C2/C3 分別測試條件；保留 Ed.1 向後相容
- **feat**: DNV 新增 DNVGL-CG-0339:2019 Class A/B/C/D（含穩態/循環濕熱區分）；保留舊版 Std.Cert.2.4
- **feat**: KEMA 新增乾熱/冷測/濕熱穩態/溫度循環四項測試
- **feat**: NMEA 細分受保護/暴露裝置，NMEA 0183/2000 獨立版本
- **feat**: `STANDARDS_AND_SOPS` 改由 `_build_flat_standards()` 自動展開（向後相容）
- **feat**: `GET /api/sop/standards/tree` 新端點，回傳完整三層結構供前端使用
- **feat**: `sop.py` 更新配合新 `STANDARDS_AND_SOPS` 展開方式
- **perf**: `device_data` 寫入頻率從每秒改為每 10 秒，減少 90% 寫入量
- **feat**: `_cleanup_old_data()` 自動清理 7 天前舊數據
- **feat**: CSV 報告下載按鈕（儲存紀錄後顯示）
- **fix**: CSV 報告編碼改為 big5，解決 macOS Excel 中文亂碼
- **fix**: CSV 報告溫度數值 `round(value, 2)` 防止浮點精度問題
- **feat**: 報告容差從各標準 `temp_tolerance`/`humi_tolerance` 讀取（非寫死 ±2°C）

### 2026-03-03
- **fix**: `include_router` 移至應用層級，修復重複 import（`main.py`）
- **fix**: 物理模擬目標溫度改從 `get_standard()` 讀取（`main.py`）
- **fix**: Dashboard 六種狀態正確顯示任務名稱（`Dashboard.jsx`）
- **fix**: `FINISHING` 降溫完成後自動回 `IDLE`（`main.py`）
- **fix**: 暫停切換改為 `RUNNING ↔ PAUSED` 真正切換（`main.py`）
- **feat**: `SopResponse` 新增 `standard_id` 欄位（`sop.py`）
- **feat**: Pydantic `StartSopRequest` 輸入驗證（`sop.py`）
- **feat**: 上架驗證注意事項確認框（`SOPPage.jsx`）
- **feat**: 待機/執行中畫面自動切換邏輯（`SOPPage.jsx`）
- **feat**: SOP 步驟清單，啟動後自動勾選 Step 1、2（`SOPPage.jsx`）
- **feat**: 註冊 `sop_execution` router，支援執行紀錄 API（`main.py`）
- **feat**: ISO 17025 格式測試報告（`reports.py`）
- **refactor**: `standards.py` 統一步驟為 4 步，移除「啟動測試」步驟
- **refactor**: `init_db()` 合併進 `models.py`，`database.py` 改為轉發層
- **fix**: `datetime.utcnow` 改為 `datetime.now(timezone.utc)`（Python 3.12 相容）

### 2026-03-02
- 整合 EN50155、IEC60068 環境測試標準
- 動態 SOP 管理系統
- 前端 SOP 列表動態載入