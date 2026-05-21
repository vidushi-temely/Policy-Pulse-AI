import React, { useState, useEffect } from 'react';
import axios from 'axios';
import PlotlyComponent from 'react-plotly.js';
const Plot = PlotlyComponent.default || PlotlyComponent;
import { Sparkles, BarChart, Check, Settings } from 'lucide-react';

const Predictive = ({ scheme, state }) => {
  // Manual slider states
  const [budget, setBudget] = useState(500);
  const [manualData, setManualData] = useState(null);

  // AI Optimizer states
  const [optPool, setOptPool] = useState(1500);
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [optLoading, setOptLoading] = useState(false);

  // Load manual predictive baseline
  useEffect(() => {
    const fetchPredictive = async () => {
      if (!scheme || !state) return;
      try {
        const res = await axios.get(`http://127.0.0.1:8000/api/predictive?scheme=${encodeURIComponent(scheme)}&state=${encodeURIComponent(state)}&additional_budget=${budget}`);
        setManualData(res.data);
      } catch (error) {
        console.error("Error fetching predictive data", error);
      }
    };
    fetchPredictive();
  }, [scheme, state, budget]);

  // Solve dynamic mathematical allocation
  const handleSolveOptimization = async () => {
    if (!scheme || optPool <= 0) return;
    setOptLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/api/predictive/optimize', {
        scheme: scheme,
        additional_budget: optPool
      });
      setOptimizationResult(res.data);
    } catch (error) {
      console.error("Error solving optimization", error);
    }
    setOptLoading(false);
  };

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem' }}>
      <div>
        <h3 style={{ color: 'var(--accent)', marginBottom: '0.4rem', fontFamily: 'Outfit', fontWeight: 700 }}>🔮 Predictive Impact Simulator</h3>
        <p style={{ color: 'var(--text-secondary)', fontWeight: 500 }}>Model financial scenarios to project citizens impacted and perform automated funding optimizations.</p>
      </div>

      {/* Grid: Left is manual state-specific simulator, Right is AI national optimization solver */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr', gap: '2.5rem' }}>
        
        {/* Manual Simulator */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          <div className="glass" style={{ padding: '1.75rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
            <h4 style={{ marginBottom: '1.25rem', color: '#1e293b', fontFamily: 'Outfit', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Settings size={18} color="var(--accent)" />
              State Scenario: {state}
            </h4>
            <div className="input-group">
              <label style={{ color: '#475569', fontWeight: 700 }}>Inject Additional Budget: ₹{budget} Cr</label>
              <input 
                type="range" 
                min="0" 
                max="5000" 
                step="100" 
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                style={{ width: '100%', margin: '1.25rem 0', accentColor: 'var(--accent)' }}
              />
            </div>
            {manualData && (
              <div style={{ marginTop: '1rem', padding: '1.1rem', background: 'var(--accent-light)', borderRadius: '12px', border: '1.5px solid #cbd5e1' }}>
                <p style={{ color: 'var(--accent)', fontSize: '0.88rem', fontWeight: 700, lineHeight: 1.5 }}>
                  <strong>Historical Reach Efficiency:</strong> {manualData.efficiency.toLocaleString('en-IN', {maximumFractionDigits:0})} beneficiaries reached per ₹1 Crore deployed.
                </p>
              </div>
            )}
          </div>

          {manualData && (
            <div className="glass" style={{ padding: '1.75rem', background: '#ffffff', border: '1px solid #e2e8f0' }}>
              <h4 style={{ marginBottom: '1.25rem', color: '#1e293b', fontFamily: 'Outfit', fontWeight: 700 }}>Projected State Impact</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                <div style={{ padding: '1.1rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>New Beneficiaries Reached</p>
                  <p style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--success)' }}>
                    +{manualData.projected_new_beneficiaries.toLocaleString('en-IN', {maximumFractionDigits:0})}
                  </p>
                  <p style={{ color: 'var(--success)', fontSize: '0.78rem', fontWeight: 700, marginTop: '0.2rem' }}>Projected Growth</p>
                </div>
                <div style={{ padding: '1.1rem', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>Total Projected Reach</p>
                  <p style={{ fontSize: '1.6rem', fontWeight: '800', color: 'var(--accent-blue)' }}>
                    {manualData.total_projected_beneficiaries.toLocaleString('en-IN', {maximumFractionDigits:0})}
                  </p>
                  <p style={{ color: 'var(--accent-blue)', fontSize: '0.78rem', fontWeight: 700, marginTop: '0.2rem' }}>
                    {((manualData.total_projected_beneficiaries / manualData.current_beneficiaries - 1) * 100).toFixed(1)}% Increase
                  </p>
                </div>
              </div>

              <div style={{ height: '240px' }}>
                <Plot
                  data={[{
                    type: 'bar',
                    x: ['Current Baseline', 'Projected Future'],
                    y: [manualData.current_beneficiaries, manualData.total_projected_beneficiaries],
                    marker: { color: ['#94a3b8', '#4f46e5'], line: { width: 1, color: '#ffffff' } },
                    text: [manualData.current_beneficiaries.toLocaleString('en-IN'), manualData.total_projected_beneficiaries.toLocaleString('en-IN')],
                    textposition: 'auto',
                    textfont: { color: '#ffffff', weight: 'bold' }
                  }]}
                  layout={{
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    margin: { t: 10, b: 30, l: 50, r: 10 },
                    font: { color: '#475569', family: 'Plus Jakarta Sans' },
                    xaxis: { linecolor: '#cbd5e1' },
                    yaxis: { gridcolor: '#e2e8f0', linecolor: '#cbd5e1' },
                    autosize: true
                  }}
                  useResizeHandler={true}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false }}
                />
              </div>
            </div>
          )}
        </div>

        {/* AI Solver */}
        <div className="glass" style={{ padding: '2rem', background: '#ffffff', border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <h4 style={{ color: '#1e293b', fontFamily: 'Outfit', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
              <Sparkles size={18} color="var(--accent)" />
              National AI Budget Allocation Solver
            </h4>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>
              Input a national pool of budget. The AI mathematically distributes resources across the most efficient states to maximize country-wide citizen reach.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <div style={{ flex: 1 }} className="input-group">
              <label style={{ fontSize: '0.8rem', fontWeight: 700 }}>National Additional Pool (₹ Crores)</label>
              <input 
                type="number" 
                value={optPool}
                onChange={(e) => setOptPool(Math.max(0, Number(e.target.value)))}
                style={{ padding: '0.85rem 1rem', borderRadius: '12px', border: '1px solid #cbd5e1', fontWeight: 600, fontSize: '0.95rem', outline: 'none' }}
              />
            </div>
            <button 
              className="optimize-btn" 
              onClick={handleSolveOptimization} 
              style={{ alignSelf: 'flex-end', height: '48px' }}
              disabled={optLoading}
            >
              {optLoading ? 'Solving...' : 'Run Solver Algorithm'}
            </button>
          </div>

          {optimizationResult && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', animation: 'fadeIn 0.3s ease-out forwards' }}>
              <div style={{ padding: '1.1rem', background: '#ecfdf5', border: '1.5px solid #a7f3d0', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <Check size={28} color="var(--success)" style={{ strokeWidth: 3 }} />
                <div>
                  <p style={{ color: '#065f46', fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase' }}>Optimization Success</p>
                  <p style={{ color: '#047857', fontSize: '1.15rem', fontWeight: 800 }}>
                    Projected Reach: +{optimizationResult.total_projected_new_beneficiaries.toLocaleString('en-IN')} citizens
                  </p>
                </div>
              </div>

              {/* Table */}
              <div style={{ overflowX: 'auto' }}>
                <table className="optimize-table">
                  <thead>
                    <tr>
                      <th>State</th>
                      <th>Current Budget</th>
                      <th>AI Rec. Increment</th>
                      <th>Projected Gain</th>
                    </tr>
                  </thead>
                  <tbody>
                    {optimizationResult.allocations.slice(0, 5).map((row, idx) => (
                      <tr key={idx}>
                        <td style={{ fontWeight: 700 }}>{row.state}</td>
                        <td>₹{row.current_budget.toLocaleString('en-IN')} Cr</td>
                        <td style={{ color: 'var(--accent)', fontWeight: 700 }}>+₹{row.allocated_increment.toLocaleString('en-IN')} Cr</td>
                        <td style={{ color: 'var(--success)', fontWeight: 700 }}>+{row.projected_new_beneficiaries.toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Stacked Allocation recommendations chart */}
              <div style={{ height: '220px' }}>
                <Plot
                  data={[{
                    type: 'bar',
                    x: optimizationResult.allocations.slice(0, 6).map(a => a.state),
                    y: optimizationResult.allocations.slice(0, 6).map(a => a.allocated_increment),
                    marker: { color: '#4f46e5', line: { width: 1, color: '#ffffff' } },
                    text: optimizationResult.allocations.slice(0, 6).map(a => `₹${a.allocated_increment} Cr`),
                    textposition: 'auto',
                    textfont: { color: '#ffffff', weight: 'bold', size: 10 }
                  }]}
                  layout={{
                    title: { text: 'Optimal Budget Redistribution (Top 6 States)', font: { size: 12, family: 'Outfit', weight: 'bold' } },
                    paper_bgcolor: 'rgba(0,0,0,0)',
                    plot_bgcolor: 'rgba(0,0,0,0)',
                    margin: { t: 30, b: 30, l: 40, r: 10 },
                    font: { color: '#475569', family: 'Plus Jakarta Sans' },
                    xaxis: { linecolor: '#cbd5e1' },
                    yaxis: { gridcolor: '#e2e8f0', linecolor: '#cbd5e1', title: 'Rec. Budget Increment (Cr)' },
                    autosize: true
                  }}
                  useResizeHandler={true}
                  style={{ width: '100%', height: '100%' }}
                  config={{ displayModeBar: false }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Predictive;
