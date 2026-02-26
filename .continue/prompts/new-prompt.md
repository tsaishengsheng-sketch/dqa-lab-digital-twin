---
---
name: Unit Test Expert
description: 針對 DQA LAB 數位雙生平台撰寫高品質、覆蓋邊界情況的非同步單元測試。
invokable: true
---

請為這段程式碼撰寫一套完整的單元測試組合。請遵循以下 DQA LAB 專案開發規範：

### 1. 測試框架要求
* **工具**：使用 `pytest` 搭配 `pytest-asyncio`（針對 FastAPI 與 Simulator 的非同步特性）。
* **Mocking**：針對硬體串口 (`Serial`) 與虛擬橋接器 (`socat`)，必須使用 `unittest.mock` 進行模擬，嚴禁在測試期間開啟真實硬體端口。

### 2. 核心測試覆蓋點 (Edge Cases)
* **物理模擬引擎**：
    * **目標值趨近**：測試溫度從 25°C 上升至 100°C 時，斜率是否符合熱力學邏輯。
    * **數值跳變防禦**：模擬目標值突然改變（例如從 100°C 降為 0°C），確認系統不會產生非物理性的數值瞬間跳變。
* **FastAPI 接口**：
    * 測試 `/api/stop/emergency` 是否能在任何狀態下強制中斷模擬並回傳 `200 OK`。
    * 測試 `/api/latest` 在輪詢失敗或緩存 (`AICM_CACHE`) 為空時的異常處理。
* **硬體通訊**：
    * 測試串口讀取超時 (Timeout) 或收到亂碼字串時的重連機制。

### 3. 輸出格式
* 檔案命名請符合專案結構（例如：`tests/test_simulator.py`）。
* 每個測試案例須附帶中文註釋，解釋該測試點的物理或業務邏輯意義。
* 使用 `// ... existing code ...` 保持程式碼簡潔，僅輸出建議與演示用的代碼塊。

請根據目前 @codebase 的上下文開始撰寫。
---

Please write a thorough suite of unit tests for this code, making sure to cover all relevant edge cases