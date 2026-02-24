.PHONY: dev clean help

help:
	@echo "可用指令："
	@echo "  make dev    - 啟動模擬器、後端 API 與前端網頁"
	@echo "  make clean  - 強制清理所有殘留程序 (socat, python, node)"

dev:
	@bash dev_start.sh

clean:
	@echo "🧹 正在強制清理所有程序..."
	@pkill -f "socat" || true
	@pkill -f "main.py" || true
	@pkill -f "uvicorn" || true
	@pkill -f "node" || true
	@rm -f .socat_info.log
	@echo "✨ 清理完成"