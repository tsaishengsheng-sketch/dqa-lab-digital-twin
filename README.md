# DQA Lab Digital Twin

這是一個基於 Python 與 FastAPI 的數位孿生專案，模擬實驗室設備（如溫箱）的數據採集與顯示。

## 🌟 專案亮點
- **硬體模擬**: 使用 `socat` 建立虛擬串口對，在沒有實體設備的情況下模擬 RS232 通訊。
- **異步後端**: 使用 FastAPI 配合多執行緒 `SerialReader` 實時監聽串口數據並存入 SQLite。
- **現代前端**: 使用 Vite + React/Vue 呈現即時監控面板。
- **自動化開發環境**: 透過 `Makefile` 一鍵啟動所有服務（模擬器、API、前端、虛擬串口）。

## 🛠️ 快速啟動
此專案已封裝自動化腳本，請確保環境已安裝 `socat`。

```bash
# 啟動所有開發環境
make dev

# 強制停止並清理所有程序
make clean