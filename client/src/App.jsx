import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard';
import SOPPage from './SOPPage';

function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* 導航列 */}
        <nav style={{ 
          padding: '1rem 2rem', 
          backgroundColor: '#1e293b', 
          display: 'flex', 
          gap: '2rem',
          borderBottom: '1px solid #334155'
        }}>
          <Link to="/" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>儀表板</Link>
          <Link to="/sop" style={{ color: 'white', textDecoration: 'none', fontWeight: 'bold' }}>SOP 執行</Link>
        </nav>

        {/* 主要內容：不要給 display: flex，直接讓內容自適應寬度 */}
        <main style={{ width: '100%', flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/sop" element={<SOPPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;