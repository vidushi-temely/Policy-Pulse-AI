import React from 'react';
import { Download, Activity, FileText, Settings, Sparkles } from 'lucide-react';

const Sidebar = ({ 
  schemes, 
  states, 
  selectedScheme, 
  selectedState, 
  onSchemeChange, 
  onStateChange,
  data
}) => {
  const downloadReport = () => {
    if (!data) return;
    const { scheme, state, metrics, ai_brief } = data;
    const content = `GOVERNMENT INTELLIGENCE REPORT
==============================
Scheme: ${scheme}
State: ${state}

FINANCIAL OVERVIEW:
- Allocated Budget: Rs. ${metrics.funds_allocated.toLocaleString('en-IN', {maximumFractionDigits:2})} Cr
- Funds Utilized: Rs. ${metrics.funds_spent.toLocaleString('en-IN', {maximumFractionDigits:2})} Cr
- Utilization Rate: ${metrics.utilization}%

IMPACT METRICS:
- Total Beneficiaries Reached: ${metrics.beneficiaries.toLocaleString('en-IN')}

AI DIAGNOSTIC BRIEF:
${data.clean_brief}

*Generated autonomously by PolicyPulse AI Engine*`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${state}_${scheme}_Report.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (utilization) => {
    if (utilization < 60) return 'var(--danger)';
    if (utilization < 85) return 'var(--warning)';
    return 'var(--success)';
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header" style={{ marginBottom: '1rem' }}>
        <Activity color="var(--accent)" size={28} style={{ strokeWidth: 2.5 }} />
        <h2>Control Panel</h2>
      </div>

      <div className="input-group">
        <label><Settings size={14} /> Select Scheme</label>
        <select 
          value={selectedScheme} 
          onChange={(e) => onSchemeChange(e.target.value)}
        >
          {schemes.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="input-group">
        <label><Settings size={14} /> Target State</label>
        <select 
          value={selectedState} 
          onChange={(e) => onStateChange(e.target.value)}
        >
          {states.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>

      <div className="divider" style={{ margin: '1.5rem 0' }}></div>

      <div className="sidebar-header" style={{ marginBottom: '0.75rem' }}>
        <FileText color="var(--text-secondary)" size={20} />
        <h3 style={{ color: 'var(--text-primary)', fontSize: '1rem', fontFamily: 'Outfit', fontWeight: 700 }}>
          Automated Briefing
        </h3>
      </div>

      {data && (
        <div className="ai-card" style={{ borderLeftColor: getStatusColor(data.metrics.utilization) }}>
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.92rem' }}>
            <Sparkles size={14} color="var(--accent)" />
            {selectedState} AI Brief
          </h3>
          <div className="budget-info">
            <span>Allocated: ₹{data.metrics.funds_allocated.toLocaleString('en-IN', {maximumFractionDigits: 0})} Cr</span>
            <span style={{ color: getStatusColor(data.metrics.utilization), fontWeight: 'bold' }}>
              {data.metrics.utilization}% Utilized
            </span>
          </div>
          <div className="divider" style={{ margin: '0.6rem 0' }}></div>
          <p className="brief-text">{data.clean_brief}</p>
        </div>
      )}

      {data && (
        <button className="download-btn" onClick={downloadReport} style={{ marginTop: 'auto' }}>
          <Download size={16} />
          Download Text Report
        </button>
      )}
    </div>
  );
};

export default Sidebar;
