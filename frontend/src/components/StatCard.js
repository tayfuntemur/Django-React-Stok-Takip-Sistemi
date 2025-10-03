import React from 'react';

function StatCard({ title, value, icon, color, loading }) {
  return (
    <div 
      className="card stat-card" 
      style={{ borderLeft: `4px solid ${color}` }}
    >
      <div 
        className="stat-icon" 
        style={{ background: color }}
      >
        {icon}
      </div>
      <div className="stat-details">
        <div className="stat-title">{title}</div>
        {loading ? (
          <div className="stat-value-loading">Yükleniyor...</div>
        ) : (
          <div className="stat-value">{value}</div>
        )}
      </div>
    </div>
  );
}

export default StatCard;