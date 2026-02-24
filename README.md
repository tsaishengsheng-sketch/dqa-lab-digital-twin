# DQA Lab Digital Twin

這是一個基於 Python 與 FastAPI 的數位孿生專案，模擬實驗室設備（如溫箱）的數據採集與顯示。

## 🌟 專案亮點
- **硬體模擬**: 使用 `socat` 建立虛擬串口對，在沒有實體設備的情況下模擬 RS232 通訊。
- **異步後端**: 使用 FastAPI 配合多執行緒 `SerialReader` 實時監聽串口數據並存入 SQLite。
- **現代前端**: 使用 Vite + React/Vue 呈現即時監控面板。
- **自動化開發環境**: 透過 `Makefile` 一鍵啟動所有服務（模擬器、API、前端、虛擬串口）。

## 🏗️ 系統架構

本專案採用分層架構設計，確保硬體通訊與業務邏輯解耦。

```mermaid
graph TD
    subgraph "Client Side (React + Vite)"
        A[Dashboard]
        B[SOP Execution]
        C[...Future Modules]
    end

    subgraph "Backend Server (FastAPI)"
        D[API Routes]
        E[Service Layer]
        F[(SQLite Database)]
        D --> E
        E --> F
    end

    subgraph "Hardware Communication"
        G[SerialReader Service]
        H{socat Virtual Bridge}
    end

    subgraph "Device Simulation"
        I[Kson Chamber Sim]
        J[...Future Simulators]
    end

    %% 連線關係
    A & B --> D
    E --> G
    G <--> H
    H <--> I & J
    ```
    
## 🛠️ 快速啟動
此專案已封裝自動化腳本。在開始之前，請確保環境已安裝 `socat`。(用於虛擬串口模擬）)

```bash

# 1. 安裝環境與依賴:
# 第一次執行時，請先安裝所有後端、模擬器與前端的依賴

make install

# 2. 環境變數設定:
# 將根目錄的 .env.example 複製一份並命名為 .env，這是啟動模擬器與後端 API 的必要步驟：

cp .env.example .env

# 3. 一鍵啟動開發服務:使用 Makefile 指令自動建立虛擬串口、啟動後端與前端：

make dev

# 4.停止與清理 結束開發後，按一下 Ctrl + C 即可停止。若需清理殘留程序，請執行:

make clean