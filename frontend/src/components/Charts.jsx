import React, { useEffect, useState } from 'react';
import PlotlyComponent from 'react-plotly.js';
const Plot = PlotlyComponent.default || PlotlyComponent;
import axios from 'axios';

const Charts = ({ scheme }) => {
  const [topStates, setTopStates] = useState([]);
  const [comparison, setComparison] = useState([]);

  useEffect(() => {
    const fetchCharts = async () => {
      if (!scheme) return;
      try {
        const [topRes, compRes] = await Promise.all([
          axios.get(`http://127.0.0.1:8000/api/analytics/top-states?scheme=${encodeURIComponent(scheme)}`),
          axios.get(`http://127.0.0.1:8000/api/analytics/comparison`)
        ]);
        setTopStates(topRes.data);
        setComparison(compRes.data);
      } catch (error) {
        console.error("Error fetching charts", error);
      }
    };
    fetchCharts();
  }, [scheme]);

  return (
    <section className="card" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="chart-container glass" style={{ height: '400px', padding: '1.5rem' }}>
        <h3 style={{ color: 'var(--accent)', marginBottom: '1rem', fontFamily: 'Outfit', fontWeight: 700 }}>🏆 Top 5 Performing States</h3>
        <Plot
          data={[{
            type: 'bar',
            x: topStates.map(d => d.State),
            y: topStates.map(d => d.Utilization),
            marker: { 
              color: topStates.map(d => d.Utilization), 
              colorscale: 'Viridis',
              line: { width: 1.5, color: '#ffffff' }
            },
            text: topStates.map(d => `${d.Utilization.toFixed(1)}%`),
            textposition: 'auto',
            textfont: { color: '#ffffff', weight: 'bold' }
          }]}
          layout={{
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 10, b: 60, l: 50, r: 10 },
            font: { color: '#475569', family: 'Plus Jakarta Sans' },
            xaxis: { 
              tickangle: -30, 
              gridcolor: '#f1f5f9',
              linecolor: '#cbd5e1'
            },
            yaxis: { 
              gridcolor: '#e2e8f0', 
              zerolinecolor: '#cbd5e1',
              title: 'Utilization %'
            },
            autosize: true
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: 'calc(100% - 40px)' }}
          config={{ displayModeBar: false }}
        />
      </div>

      <div className="chart-container glass" style={{ height: '450px', padding: '1.5rem' }}>
        <h3 style={{ color: 'var(--accent)', marginBottom: '1rem', fontFamily: 'Outfit', fontWeight: 700 }}>📊 Macro-Economic Scheme Comparison</h3>
        <Plot
          data={[
            {
              type: 'bar',
              name: 'Funds Allocated',
              x: comparison.map(d => d.Scheme),
              y: comparison.map(d => d.Funds_Allocated),
              marker: { color: '#4f46e5', line: { width: 1.5, color: '#ffffff' } }
            },
            {
              type: 'bar',
              name: 'Funds Spent',
              x: comparison.map(d => d.Scheme),
              y: comparison.map(d => d.Funds_Spent),
              marker: { color: '#10b981', line: { width: 1.5, color: '#ffffff' } }
            }
          ]}
          layout={{
            barmode: 'group',
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            margin: { t: 10, b: 60, l: 60, r: 10 },
            font: { color: '#475569', family: 'Plus Jakarta Sans' },
            xaxis: { gridcolor: '#f1f5f9', linecolor: '#cbd5e1' },
            yaxis: { gridcolor: '#e2e8f0', linecolor: '#cbd5e1', title: 'Amount (in Crores)' },
            legend: { x: 0.5, y: 1.15, orientation: 'h', xanchor: 'center' },
            autosize: true
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: 'calc(100% - 40px)' }}
          config={{ displayModeBar: false }}
        />
      </div>
    </section>
  );
};

export default Charts;
