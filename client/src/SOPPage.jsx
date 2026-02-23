import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SOPPage.css';

// 圖標元件
const CheckIcon = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 6L9 17l-5-5"/></svg>;
const UploadIcon = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>;

// 全域欄位中文標籤對照表（用於參數表單）
const FIELD_LABELS = {
  product_model: '產品型號',
  quantity: '數量',
  program_name: '程式名稱',
  is_new: '是否為新程式',
  protect_temp: '保護溫度 (°C)',
  jump_to_step: '跳段步驟號',
  step_number: '步驟號',
  temperature: '溫度 (°C)',
  humidity: '濕度 (%)',
  hold_time: '停留時間 (分鐘)',
  ts1: '時序插座 TS1',
  ts2: '時序插座 TS2',
  ts3: '時序插座 TS3',
  steps: '程式步驟'
};

const FIELD_PLACEHOLDERS = {
  product_model: '例: EDS-2000',
  quantity: '例: 3',
  program_name: '例: high_temp_test',
  is_new: '是/否',
  protect_temp: '例: 95',
  jump_to_step: '例: 5',
  step_number: '例: 1',
  temperature: '例: 85',
  humidity: '例: 40',
  hold_time: '例: 30'
};

function SOPPage() {
  const [sopList, setSopList] = useState([]);
  const [selectedSop, setSelectedSop] = useState(null);
  const [completedSteps, setCompletedSteps] = useState({});
  const [stepParams, setStepParams] = useState({});
  const [stepPhotos, setStepPhotos] = useState({});

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/sop/')
      .then(res => setSopList(res.data))
      .catch(err => console.error('後端載入失敗', err));
  }, []);

  const loadSop = (sopId) => {
    axios.get(`http://127.0.0.1:8000/api/sop/${sopId}`)
      .then(res => {
        setSelectedSop(res.data);
        setCompletedSteps({});
        setStepParams({});
        setStepPhotos({});
      })
      .catch(err => console.error('載入 SOP 失敗', err));
  };

  const toggleStep = (stepId) => {
    setCompletedSteps(prev => ({ ...prev, [stepId]: !prev[stepId] }));
  };

  const handleParamChange = (stepId, field, value) => {
    setStepParams(prev => ({
      ...prev,
      [stepId]: { ...prev[stepId], [field]: value }
    }));
  };

  const handlePhotoUpload = (stepId, e) => {
    const file = e.target.files[0];
    if (file) {
      const previewUrl = URL.createObjectURL(file);
      setStepPhotos(prev => ({
        ...prev,
        [stepId]: [...(prev[stepId] || []), previewUrl]
      }));
    }
  };

  // 遞迴渲染參數表單（支援嵌套物件與陣列）
  const renderParameterField = (stepId, fieldName, fieldSchema, value = '', onChange) => {
    const { type, title, properties, items } = fieldSchema;

    if (type === 'object' && properties) {
      return (
        <div key={fieldName} style={{ marginLeft: '20px', borderLeft: '2px solid var(--border)', paddingLeft: '15px', marginBottom: '15px' }}>
          <div style={{ fontWeight: '600', marginBottom: '8px', color: 'var(--accent)' }}>{title || FIELD_LABELS[fieldName] || fieldName}</div>
          {Object.keys(properties).map(subField => (
            <div key={subField} style={{ marginBottom: '12px' }}>
              {renderParameterField(stepId, subField, properties[subField], value?.[subField], (newVal) => {
                onChange({ ...value, [subField]: newVal });
              })}
            </div>
          ))}
        </div>
      );
    } else if (type === 'array' && items) {
      const arrayValue = Array.isArray(value) ? value : [];
      return (
        <div key={fieldName} style={{ marginBottom: '15px' }}>
          <div style={{ fontWeight: '600', marginBottom: '8px', color: 'var(--accent)' }}>{title || FIELD_LABELS[fieldName] || fieldName}</div>
          {arrayValue.map((item, index) => (
            <div key={index} style={{ marginBottom: '10px', padding: '10px', background: 'rgba(0,0,0,0.1)', borderRadius: '6px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span>項目 {index + 1}</span>
                <button onClick={() => {
                  const newArray = [...arrayValue];
                  newArray.splice(index, 1);
                  onChange(newArray);
                }} style={{ background: 'none', border: 'none', color: 'red', cursor: 'pointer' }}>刪除</button>
              </div>
              {Object.keys(items.properties).map(subField => (
                <div key={subField} style={{ marginBottom: '8px' }}>
                  {renderParameterField(stepId, subField, items.properties[subField], item[subField], (newVal) => {
                    const newArray = [...arrayValue];
                    newArray[index] = { ...newArray[index], [subField]: newVal };
                    onChange(newArray);
                  })}
                </div>
              ))}
            </div>
          ))}
          <button onClick={() => {
            const newItem = {};
            if (items.properties) {
              Object.keys(items.properties).forEach(key => {
                const prop = items.properties[key];
                if (prop.type === 'array') newItem[key] = [];
                else if (prop.type === 'object') newItem[key] = {};
                else if (prop.type === 'integer') newItem[key] = 0;
                else if (prop.type === 'number') newItem[key] = 0.0;
                else if (prop.type === 'boolean') newItem[key] = false;
                else newItem[key] = '';
              });
            }
            onChange([...arrayValue, newItem]);
          }} style={{ padding: '5px 10px', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '4px', cursor: 'pointer' }}>
            + 新增項目
          </button>
        </div>
      );
    } else {
      const inputType = type === 'integer' || type === 'number' ? 'number' : 'text';
      return (
        <div key={fieldName} style={{ marginBottom: '8px' }}>
          <label style={{ display: 'block', fontSize: '0.9rem', fontWeight: '500', color: 'var(--text-secondary)', marginBottom: '4px' }}>
            {title || FIELD_LABELS[fieldName] || fieldName}
          </label>
          <input
            type={inputType}
            value={value ?? ''}
            onChange={(e) => {
              if (type === 'number' || type === 'integer') {
                const num = parseFloat(e.target.value);
                if (isNaN(num) || num < 0) {
                  onChange(0);
                } else {
                  onChange(num);
                }
              } else {
                onChange(e.target.value);
              }
            }}
            min="0"
            step={type === 'integer' ? '1' : 'any'}
            placeholder={FIELD_PLACEHOLDERS[fieldName] || ''}
            style={{ padding: '6px', width: '100%', maxWidth: '300px', borderRadius: '4px', border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text-primary)' }}
          />
        </div>
      );
    }
  };

  const renderParameters = (step) => {
    if (!step.requires_parameters || !step.parameters_schema) return null;
    const { properties } = step.parameters_schema;
    return (
      <div className="param-card">
        <div className="param-title">📋 請填寫以下資訊</div>
        {Object.keys(properties).map(field => (
          <div key={field} className="param-field">
            {renderParameterField(
              step.step_id,
              field,
              properties[field],
              stepParams[step.step_id]?.[field],
              (newVal) => handleParamChange(step.step_id, field, newVal)
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderPhotoUpload = (step) => {
    if (!step.requires_photo) return null;
    const photos = stepPhotos[step.step_id] || [];
    return (
      <div className="photo-upload">
        <div className="photo-grid">
          {photos.map((url, idx) => (
            <div key={idx} className="photo-preview" style={{ backgroundImage: `url(${url})` }} />
          ))}
          <label className="photo-upload-btn">
            <UploadIcon />
            <input type="file" accept="image/*" onChange={(e) => handlePhotoUpload(step.step_id, e)} style={{ display: 'none' }} />
            <span>上傳照片</span>
          </label>
        </div>
      </div>
    );
  };

  if (!selectedSop) {
    return (
      <div className="sop-container">
        <h1 className="sop-title">選擇要執行的測試方法</h1>
        <div className="sop-list">
          {sopList.map(sop => (
            <button key={sop.sop_id} className="sop-card" onClick={() => loadSop(sop.sop_id)}>
              <span className="sop-name">{sop.name}</span>
              <span className="sop-meta">{sop.test_type}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  const totalSteps = selectedSop.steps.length;
  const completedCount = Object.values(completedSteps).filter(Boolean).length;

  return (
    <div className="sop-container">
      <div className="sop-header">
        <button className="back-btn" onClick={() => setSelectedSop(null)}>← 返回</button>
        <div className="header-info">
          <h2>{selectedSop.name} <span className="sop-version">v{selectedSop.version}</span></h2>
          <div className="progress-indicator">
            <div className="progress-bar" style={{ width: `${(completedCount / totalSteps) * 100}%` }} />
            <span>{completedCount}/{totalSteps} 步驟</span>
          </div>
        </div>
      </div>

      <div className="steps-list">
        {selectedSop.steps.map(step => (
          <div key={step.step_id} className={`step-card ${completedSteps[step.step_id] ? 'completed' : ''}`}>
            <div className="step-header">
              <div className="step-checkbox">
                <input
                  type="checkbox"
                  id={`step-${step.step_id}`}
                  checked={!!completedSteps[step.step_id]}
                  onChange={() => toggleStep(step.step_id)}
                />
                <label htmlFor={`step-${step.step_id}`} className="checkbox-label">
                  {completedSteps[step.step_id] && <CheckIcon />}
                </label>
              </div>
              <div className="step-title">
                <h3>{step.step_id}. {step.name}</h3>
                {step.optional && <span className="step-badge optional">可選</span>}
              </div>
            </div>
            <p className="step-description">{step.description}</p>
            {renderParameters(step)}
            {renderPhotoUpload(step)}
          </div>
        ))}
      </div>

      <div className="sop-footer">
        <button className="complete-btn" onClick={() => alert('SOP 完成！可輸出報告')}>
          完成 SOP
        </button>
      </div>
    </div>
  );
}

export default SOPPage;