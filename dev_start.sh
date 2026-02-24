#!/bin/bash
# dev_start.sh

LOG_FILE=".socat_info.log"

cleanup() {
    echo -e "\n\n👋 正在關閉所有開發服務 (含前端)..."
    kill $BACK_PID $SIM_PID $SOCAT_PID $CLIENT_PID 2>/dev/null
    pkill -P $$ 2>/dev/null
    rm -f "$LOG_FILE"
    exit
}
trap cleanup SIGINT SIGTERM EXIT

# 1. 建立串口
echo "🔗 正在建立虛擬串口..."
socat -d -d pty,raw,echo=0 pty,raw,echo=0 2> "$LOG_FILE" &
SOCAT_PID=$!
sleep 1 

# 2. 解析路徑
PTYS=$(grep -o "/dev/ttys[0-9]*" "$LOG_FILE" | tail -n 2)
PTY_A=$(echo $PTYS | awk '{print $1}')
PTY_B=$(echo $PTYS | awk '{print $2}')

if [[ -z "$PTY_A" || -z "$PTY_B" ]]; then echo "❌ 串口建立失敗"; exit 1; fi

echo "✅ 模擬器: $PTY_A | 後端: $PTY_B"

# 3. 啟動程序
echo "🚀 啟動模擬器..."
(cd simulator && SIM_PORT="$PTY_A" python3 main.py) &
SIM_PID=$!

echo "🚀 啟動後端 API..."
(cd backend && SERIAL_PORTS="$PTY_B" uvicorn app.main:app --reload --port 8000) &
BACK_PID=$!

# --- 新增：啟動前端 Client ---
echo "🚀 啟動前端網頁 (Vite)..."
(cd client && npm run dev) &
CLIENT_PID=$!

echo "------------------------------------------------"
echo "✅ 系統已全面啟動！"
echo "🌐 前端網址: http://localhost:5173"
echo "📡 後端網址: http://127.0.0.1:8000/api/latest"
echo "💡 提示: 按下 Ctrl+C 同時停止所有服務"
echo "------------------------------------------------"

wait