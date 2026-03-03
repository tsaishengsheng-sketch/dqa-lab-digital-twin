# DQA Lab Digital Twin

基於 FastAPI + React 的實驗室數位孿生平台，整合物理模擬引擎與國際環境測試標準，實現溫箱設備的遠端自動化控制。

## 核心功能

- **物理模擬引擎** — 即時升降溫斜率模擬，遵守 EN50155、IEC60068 等標準速率限制
- **SOP 動態管理** — 從 `standards.py` 載入測試流程，`standard_id` 由後端直接回傳
- **上架安全確認** — 啟動前強制確認四項注意事項，全勾才能啟動
- **工業級控制面板** — 緊急停止、暫停切換、正常結束三鍵邏輯
- **Pydantic 輸入驗證** — API 強型別檢查，錯誤立即回傳 422

## 支持的環境測試標準

| 標準 | 測試名稱 | 溫度範圍 | 速率限制 |
|------|---------|---------|---------|
| **EN50155** | 高/低溫儲存 | -40 ~ +70°C | 5°C/min |
| **IEC60068-2-14** | 溫度循環 | -40 ~ +85°C | 2°C/min |
| **IEC60068-2-30** | 濕熱循環 | 25 ~ 55°C | 2°C/min |

## 快速啟動

```bash
# 安裝依賴
pip install -r backend/requirements.txt
npm install --prefix client

# 初始化資料庫
python backend/app/init_db.py

# 一鍵啟動
make dev
```

啟動後開啟 `http://localhost:5173/sop`，確認注意事項後選擇 SOP 啟動測試。

## API 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/latest` | 即時溫濕度與狀態 |
| GET | `/api/sop/` | SOP 列表（含 standard_id）|
| POST | `/api/sop/start` | 啟動 SOP |
| POST | `/api/stop/emergency` | 緊急停止 |
| POST | `/api/stop/pause` | 暫停 |
| POST | `/api/stop/normal` | 正常停止 |

互動式 API 文件：`http://localhost:8000/docs`

## 技術堆棧

後端：FastAPI、Pydantic、SQLAlchemy、asyncio
前端：React 18、Vite、Recharts、Axios
環境：Python 3.9+、Node.js 16+、macOS/Linux（需要 socat）

## 更新紀錄

### 2026-03-03
- **fix**: `include_router` 移至應用層級
- **fix**: 物理模擬目標溫度改從 `get_standard()` 讀取
- **fix**: Dashboard 四種狀態正確顯示任務名稱
- **feat**: `SopResponse` 新增 `standard_id` 欄位
- **feat**: Pydantic `StartSopRequest` 輸入驗證
- **feat**: 上架驗證注意事項確認框

### 2026-03-02
- 整合 EN50155、IEC60068 環境測試標準
- 動態 SOP 管理系統
- 前端 SOP 列表動態載入

## 延伸文件

- [系統架構與開發進度](./docs/architecture.md)

## 授權

MIT License