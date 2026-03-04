# 📝 Changelog

所有版本修改紀錄集中於此，依日期倒序排列。

---

## 2026-03-04（續）

- **feat**: 新增 `ErrorLog` 表（`models.py`），記錄緊急停止事件
- **feat**: 新增 `errors.py` router，`GET /api/errors/` 回傳所有異常紀錄
- **feat**: `emergency_stop()` 觸發時自動寫入 device_id、error_type、當下溫濕度、執行中 SOP（`main.py`）
- **feat**: 新增「異常看板」頁面（`ErrorLog.jsx`），顯示統計卡片與完整紀錄列表
- **feat**: `App.jsx` 導航列新增「異常看板」入口，active 頁面高亮
- **feat**: `Dashboard.jsx` 統一 GitHub dark 主題，新增執行紀錄列表與一鍵下載 CSV
- **feat**: `SOPPage.jsx` 新增即時 TEMP TREND 折線圖（含目標溫度虛線）、EMERGENCY 閃爍、狀態 badge、步驟進度條
- **fix**: 緊急停止後正常停止按鈕可用（`canStop = isActive || isEmergency`）
- **fix**: TEMP/HUMI 卡片加左側 accent 色邊框

---

## 2026-03-04

- **feat**: 新增 `docs/templates/QA_Test_Report_Template.docx` — 對外 QA 測試報告空白模板（8 章節，含封面/目錄/簽名欄，已移除商標）
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
- **docs**: 新增 `CHANGELOG.md`，集中所有版本 log
- **docs**: 新增 `AGENTS.md`（從 `docs/notes/ai_context.md` 改名並更新）
- **docs**: `README.md` 移除更新紀錄，改連結至 CHANGELOG
- **docs**: `architecture.md` 移除修改紀錄，改連結至 CHANGELOG

---

## 2026-03-03

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

---

## 2026-03-02

- 整合 EN50155、IEC60068 環境測試標準
- 動態 SOP 管理系統
- 前端 SOP 列表動態載入