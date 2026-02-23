import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// 格式化時間為台灣時區 (Asia/Taipei)
const formatTime = (timestamp) => {
  const date = new Date(timestamp + 'Z'); // 強制當作 UTC 時間解析
  return date.toLocaleTimeString('zh-TW', { 
    timeZone: 'Asia/Taipei',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

const formatDateTime = (timestamp) => {
  const date = new Date(timestamp + 'Z');
  return date.toLocaleString('zh-TW', {
    timeZone: 'Asia/Taipei',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  }).replace(/\//g, '/');
};

function Dashboard() {
  const [currentData, setCurrentData] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/latest');
        setCurrentData(res.data);
        setHistory(prev => [...prev.slice(-19), res.data]); // 保留最近20筆
      } catch (err) {
        console.error('抓取失敗', err);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const chartData = {
    labels: history.map(d => formatTime(d.timestamp)),
    datasets: [
      {
        label: '溫度 (°C)',
        data: history.map(d => d.temperature),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        yAxisID: 'y',
      },
      {
        label: '濕度 (%)',
        data: history.map(d => d.humidity),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        yAxisID: 'y1',
      }
    ],
  };

  const options = {
    responsive: true,
    interaction: { mode: 'index', intersect: false },
    scales: {
      y: { type: 'linear', display: true, position: 'left', title: { display: true, text: '溫度 (°C)' } },
      y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: '濕度 (%)' }, grid: { drawOnChartArea: false } },
    },
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>溫箱即時監控</h1>
      {currentData && (
        <div style={{ marginBottom: '20px' }}>
          <p>最新數據：</p>
          <p>溫度：{currentData.temperature}°C</p>
          <p>濕度：{currentData.humidity}%</p>
          <p>時間：{formatDateTime(currentData.timestamp)}</p>
        </div>
      )}
      <div style={{ height: '400px' }}>
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}

export default Dashboard;