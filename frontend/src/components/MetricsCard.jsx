import React from 'react';

const MetricsCard = ({ title, value, subtitle }) => {
  return (
    <div className="metric-card glass">
      <span className="metric-label">{title}</span>
      <span className="metric-value">{value}</span>
      <span className="metric-subtitle">{subtitle}</span>
    </div>
  );
};

export default MetricsCard;
