# DQA Lab Digital Twin 控制中心
.PHONY: dev clean install help logs

# 預設顯示幫助資訊
help:
	@echo "🛠️  DQA Lab 控制指令："
	@echo "  make install - 1. 自動安裝後端、模擬器與前端依賴"
	@echo "  make dev     - 2. 一鍵啟動 (自動處理虛擬串口與所有服務)"
	@echo "  make clean   - 3. 強制關閉所有服務並清理殘留連線"
	@echo "  make logs    - 4. 查看後端即時運行日誌"

# 1. 安裝流程：加入虛擬環境檢查與前端套件補完
install:
	@echo "📦 正在檢查並安裝後端依賴 (Python)..."
	pip install -r backend/requirements.txt
	@echo "📦 正在檢查並安裝模擬器依賴 (Python)..."
	pip install -r simulator/requirements.txt
	@echo "📦 正在檢查並安裝前端依賴 (Node.js)..."
	cd client && npm install
	@echo "✅ [SUCCESS] 所有依賴已就緒！"

# 2. 啟動流程
dev:
	@echo "🚀 系統全面啟動中..."
	@bash dev_start.sh

# 3. 清理流程：更精準的程序終止與資源回收
clean:
	@echo "🧹 正在執行深度清理..."
	# 終止後端 uvicorn
	-@pkill -9 -f "uvicorn backend.app.main:app" || true
	# 終止模擬器
	-@pkill -9 -f "python3 simulator/main.py" || true
	# 終止前端 Node 服務
	-@pkill -9 -f "node.*vite" || true
	# 終止虛擬串口 socat
	-@pkill -9 -f "socat" || true
	# 刪除暫存與日誌檔
	@rm -f .socat_info.log .serial_ports.tmp
	@echo "✨ 清理完成，環境已恢復。"

# 4. 日誌追蹤：方便你即時偵錯
logs:
	@tail -f .socat_info.log