import React, { useEffect, useState } from 'react';
import PlotlyComponent from 'react-plotly.js';
const Plot = PlotlyComponent.default || PlotlyComponent;
import axios from 'axios';

const GeoMap = ({ scheme }) => {
  const [mapData, setMapData] = useState([]);
  const [geoJson, setGeoJson] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!scheme) return;
      setLoading(true);
      try {
        const [dataRes, geoRes] = await Promise.all([
          axios.get(`http://127.0.0.1:8000/api/map-data?scheme=${encodeURIComponent(scheme)}`),
          axios.get(`http://127.0.0.1:8000/api/geojson`)
        ]);
        setMapData(dataRes.data);
        setGeoJson(geoRes.data);
      } catch (error) {
        console.error("Error loading map data", error);
      }
      setLoading(false);
    };
    fetchData();
  }, [scheme]);

  if (loading) return <div className="loader-container"><div className="loader"></div><p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Loading Map Intelligence...</p></div>;
  if (!geoJson || mapData.length === 0) return <p style={{ padding: '2rem', textAlign: 'center', color: 'var(--danger)' }}>Failed to load map data.</p>;

  // Prepare custom hover text
  const hoverText = mapData.map(d => 
    `<b>${d.State}</b><br>` +
    `Beneficiaries: ${d.Beneficiaries.toLocaleString('en-IN')}<br>` +
    `Budget: ₹${d.Funds_Allocated.toLocaleString('en-IN', {maximumFractionDigits:1})} Cr<br>` +
    `Spent: ₹${d.Funds_Spent.toLocaleString('en-IN', {maximumFractionDigits:1})} Cr<br>` +
    `Utilization: <b>${d.Utilization}%</b>`
  );

  return (
    <div className="chart-container glass" style={{ height: '620px' }}>
      <Plot
        data={[{
          type: 'choropleth',
          geojson: geoJson,
          locations: mapData.map(d => d.State),
          featureidkey: 'properties.st_nm',
          z: mapData.map(d => d.Utilization),
          text: hoverText,
          hoverinfo: 'text',
          colorscale: 'Viridis',
          colorbar: { 
            title: 'Utilization %', 
            tickfont: { color: '#475569', family: 'Plus Jakarta Sans' }, 
            titlefont: { color: '#475569', family: 'Plus Jakarta Sans', size: 13, weight: 'bold' } 
          }
        }]}
        layout={{
          title: { 
            text: `📍 National Utilization Heatmap: ${scheme}`, 
            font: { color: '#0f172a', size: 18, family: 'Outfit', weight: 'bold' } 
          },
          geo: {
            fitbounds: 'locations',
            visible: false,
            bgcolor: 'rgba(0,0,0,0)'
          },
          paper_bgcolor: 'rgba(0,0,0,0)',
          plot_bgcolor: 'rgba(0,0,0,0)',
          margin: { r: 10, t: 70, l: 10, b: 10 },
          autosize: true
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ displayModeBar: false }}
      />
    </div>
  );
};

export default GeoMap;
