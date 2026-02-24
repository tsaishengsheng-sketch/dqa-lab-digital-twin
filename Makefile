.PHONY: dev clean install help

# 預設動作：顯示說明
help:
	@echo "可用指令："
	@echo "  make install - 安裝後端、模擬器與前端的所有依賴套件"
	@echo "  make dev     - 一鍵啟動所有開發環境"
	@echo "  make clean   - 強制清理殘留程序"

# 新增：自動安裝所有依賴
install:
	@echo "📦 正在安裝後端依賴..."
	pip install -r backend/requirements.txt
	@echo "📦 正在安裝模擬器依賴..."
	pip install -r simulator/requirements.txt
	@echo "📦 正在安裝前端依賴..."
	cd client && npm install
	@echo "✅ 所有依賴安裝完成！"

dev:
	@bash dev_start.sh

clean:
	@echo "🧹 正在清理程序..."
	@pkill -f "socat" || true
	@pkill -f "main.py" || true
	@pkill -f "uvicorn" || true
	@pkill -f "node" || true
	@rm -f .socat_info.log