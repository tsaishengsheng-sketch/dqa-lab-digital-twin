import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './Dashboard';
import SOPPage from './SOPPage';

function App() {
  return (
    <BrowserRouter>
      <nav style={{ padding: '10px', backgroundColor: '#1e293b', marginBottom: '20px', display: 'flex', gap: '20px' }}>
        <Link to="/" style={{ color: 'white', textDecoration: 'none' }}>儀表板</Link>
        <Link to="/sop" style={{ color: 'white', textDecoration: 'none' }}>SOP 執行</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/sop" element={<SOPPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;