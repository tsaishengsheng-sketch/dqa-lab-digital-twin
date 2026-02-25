# DQA Lab Digital Twin

這是一個基於 Python FastAPI 與 React 的實驗室數位孿生平台。本專案不只是數據採集，更結合了物理模擬引擎，實現了實驗室設備（如溫箱）的完整數位轉型與遠端自動化控制邏輯。

## 🌟 核心功能

- **✅ 工業級控制面板**: 實作「緊急停止」、「暫停切換」、「正常結束」三種狀態控制邏輯，符合真實實驗室操作安全規範。
- **✅ 物理模擬引擎**: 具備即時升降溫斜率模擬 (Temperature Slew Rate) 與數值震盪演算法，精準模擬溫箱物理行為。
- **✅ 異步通訊架構**: 採用 FastAPI 多執行緒異步處理，確保串口數據採集 (SerialReader) 與 API 回應互不干擾。
- **✅ 響應式監控介面**: 使用 Vite + React 建構，具備 Auto-Layout 功能，支援多平台視窗比例監控。
- **✅ 自動化開發環境**: 透過 `Makefile` 一鍵啟動虛擬串口橋接 (`socat`)、物理模擬器、API 與前端。

## 🏗️ 系統架構

本專案採用解耦架構，將硬體通訊層、模擬引擎層與業務邏輯層分離。

```mermaid
graph TD
    classDef default fill:#2d333b,stroke:#adbac7,color:#adbac7,stroke-width:1px;
    classDef highlight fill:#347d39,stroke:#44bc51,color:#fff,stroke-width:2px;

    subgraph "Client Side (React + Vite)"
        A[Dashboard / Chart]
        B[SOP Control Panel]
        C[Responsive Layout]
    end

    subgraph "Backend Engine (FastAPI)"
        D[State Machine Routes]
        E[Physics Sim Engine]
        F[(SQLite / Cache)]
        D --> E
        E --> F
    end

    subgraph "Hardware Layer"
        G[Async SerialReader]
        H{socat Virtual Bridge}
    end

    subgraph "Twin Simulation"
        I[Kson Physics Sim]
    end

    A & B & C --> D
    E --> G
    G <--> H
    H <--> I

    class A,B,C,D,E,F,G,H,I highlight;

```

## 🛠️ 快速啟動

```bash

# 1. 初始化環境:第一次執行請安裝依賴並設定環境變數
make install

# 2. 環境變數設定:
# 複製設定檔並命名為 .env
cp .env.example .env

# 3. 一鍵啟動開發服務:
# 自動建立虛擬串口、啟動後端 API、前端與模擬器

make dev

# 4. 停止與清理:
# 結束開發後，按一下 Ctrl + C 即可停止。若需清理殘留程序，請執行:
make clean

```

## 📁 延伸文件
- [系統完整架構細節](./architecture.md) (記錄所有模組開發進度與未來待辦事項)
