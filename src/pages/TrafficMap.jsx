import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, CloudRain, Clock, WifiOff, RefreshCw } from 'lucide-react';
import { MapContainer, TileLayer, Marker, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

import Badge from '../components/Shared/Badge';
import Button from '../components/Shared/Button';
import { useApi } from '../hooks/useApi';
import { getJunctions } from '../services/api';
import styles from './TrafficMap.module.css';

// Fix for default Leaflet icon paths in some bundlers (optional if we use custom icons only)
delete L.Icon.Default.prototype._getIconUrl;

// ── Junction status helpers ──────────────────────────────────────────────────

const statusToKey = (s) => {
  if (s === 'HIGH' || s === 'CRITICAL') return 'red';
  if (s === 'MODERATE') return 'yellow';
  return 'green';
};

const severityLabel = { red: 'Congested', yellow: 'Moderate', green: 'Low Traffic' };
const severityBadge = { red: 'red', yellow: 'yellow', green: 'green' };
const STATUS_COLOR = { red: '#ef4444', yellow: '#eab308', green: '#22c55e' };

/**
 * Custom Leaflet divIcon maker for our status-colored markers.
 */
function createMarkerIcon(color, isSelected) {
  return L.divIcon({
    className: 'custom-leaflet-marker',
    html: `
      <div style="
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: ${isSelected ? '24px' : '16px'};
        height: ${isSelected ? '24px' : '16px'};
      ">
        ${isSelected ? `<div style="position: absolute; width: 32px; height: 32px; background: ${color}; opacity: 0.25; border-radius: 50%;"></div>` : ''}
        <div style="
          background-color: ${color}; 
          width: 100%; 
          height: 100%; 
          border-radius: 50%; 
          border: 2px solid white; 
          box-shadow: 0 0 6px rgba(0,0,0,0.5);
          z-index: 10;
        "></div>
      </div>
    `,
    iconSize: isSelected ? [24, 24] : [16, 16],
    iconAnchor: isSelected ? [12, 12] : [8, 8],
  });
}

// Vadodara City Center
const CENTER_LAT = 22.3072;
const CENTER_LNG = 73.1812;

export default function TrafficMap() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState(null);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  // ── Junction data (real API) ──────────────────────────────────────────────
  const { data: apiJunctions, loading, error, refetch } = useApi(getJunctions);

  const junctions = (apiJunctions || []).map((j) => ({
    id:       j.junction_code,
    name:     j.name,
    status:   statusToKey(j.status),
    density:  j.traffic_density ?? 0,
    lat:      j.latitude,
    lng:      j.longitude,
    weather:  j.weather_condition || 'N/A',
    greenTime: j.current_green_time ?? 30,
    phase:    'N/S Green',
  }));

  const selectedJunction = junctions.find((j) => j.id === selected);

  const filtered = junctions.filter((j) => {
    const matchFilter = filter === 'all' || j.status === filter;
    const matchSearch = j.id.toLowerCase().includes(search.toLowerCase()) ||
      j.name.toLowerCase().includes(search.toLowerCase());
    return matchFilter && matchSearch;
  });

  const visibleIds = new Set(filtered.map((j) => j.id));

  return (
    <div className={styles.page}>
      {/* Map Area */}
      <div className={styles.mapWrapper} style={{ position: 'relative' }}>
        
        {/* Floating Search / Filter Panel */}
        <div className={styles.controlPanel} style={{ position: 'absolute', top: 16, left: 16, zIndex: 1000, background: 'var(--color-surface)', padding: 16, borderRadius: 8, boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
          <div className={styles.searchWrap}>
            <Search size={15} className={styles.searchIcon} />
            <input
              className={styles.searchInput}
              placeholder="Search junction..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className={styles.filterGroup}>
            <p className={styles.filterLabel}><Filter size={12} /> Filter by status</p>
            {['all', 'green', 'yellow', 'red'].map((f) => (
              <button
                key={f}
                className={[styles.filterBtn, filter === f ? styles.filterActive : ''].join(' ')}
                onClick={() => setFilter(f)}
                data-status={f}
              >
                {f === 'all' ? 'All' : severityLabel[f]}
              </button>
            ))}
          </div>
        </div>

        {/* Junction API error overlay */}
        {error && (
          <div style={{ position:'absolute', top:120, left:16, zIndex:1000,
                        background:'var(--color-surface)', border:'1px solid var(--color-border)',
                        borderRadius:8, padding:'10px 14px', display:'flex', gap:8, alignItems:'center',
                        fontSize:'var(--text-sm)', color:'var(--color-text-secondary)', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}>
            <WifiOff size={14} color="var(--color-danger)" />
            <span>{error}</span>
            <button onClick={refetch} style={{ marginLeft:8, cursor:'pointer', background:'none',
              border:'none', color:'var(--color-primary)', display:'flex', alignItems:'center', gap:4 }}>
              <RefreshCw size={12} /> Retry
            </button>
          </div>
        )}

        {/* React Leaflet Map */}
        <MapContainer 
          center={[CENTER_LAT, CENTER_LNG]} 
          zoom={13} 
          style={{ width: '100%', height: '100%', zIndex: 0 }}
          zoomControl={false}
        >
          {/* CartoDB Dark Matter or Voyager tiles can be used. Using standard OSM for now. */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {junctions.map((j) => {
            const isVisible = visibleIds.has(j.id);
            if (!isVisible) return null;
            
            const isSelected = selected === j.id;
            const color = STATUS_COLOR[j.status];

            return (
              <Marker 
                key={j.id} 
                position={[j.lat, j.lng]} 
                icon={createMarkerIcon(color, isSelected)}
                eventHandlers={{
                  click: () => setSelected(j.id)
                }}
              >
                <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                  <div style={{ textAlign: 'center' }}>
                    <strong style={{ display: 'block' }}>{j.id}</strong>
                    <span style={{ fontSize: '12px' }}>{j.name}</span>
                  </div>
                </Tooltip>
              </Marker>
            );
          })}
        </MapContainer>

        {/* Legend */}
        <div className={styles.legend} style={{ position: 'absolute', bottom: 16, left: 16, zIndex: 1000, background: 'var(--color-surface)', padding: '8px 12px', borderRadius: 8, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
          {['green', 'yellow', 'red'].map((s) => (
            <div key={s} className={styles.legendItem}>
              <span className={styles.legendDot} style={{ background: STATUS_COLOR[s] }} />
              <span>{severityLabel[s]}</span>
            </div>
          ))}
          <span className={styles.timestamp}>
            <Clock size={12} />
            {loading ? ' Loading…' : error ? ' Offline' : ` Live — ${junctions.length} junctions`}
          </span>
        </div>
      </div>

      {/* Right: Junction Detail Panel */}
      <div className={[styles.detailPanel, selectedJunction ? styles.panelOpen : ''].join(' ')}>
        {selectedJunction ? (
          <>
            <div className={styles.panelHeader}>
              <div>
                <p className={styles.panelId}>{selectedJunction.id}</p>
                <h2 className={styles.panelName}>{selectedJunction.name}</h2>
              </div>
              <Badge variant={severityBadge[selectedJunction.status]}>
                {severityLabel[selectedJunction.status]}
              </Badge>
            </div>

            <section className={styles.section}>
              <h4 className={styles.sectionTitle}>Live Traffic Data — PostgreSQL</h4>
              <div className={styles.dataGrid}>
                <DataRow label="Traffic Density"   value={`${selectedJunction.density}%`} />
                <DataRow label="Coordinates"
                  value={`${selectedJunction.lat?.toFixed(4)}, ${selectedJunction.lng?.toFixed(4)}`} />
                <DataRow label="Weather" value={selectedJunction.weather}
                  icon={<CloudRain size={13} />} />
              </div>
            </section>

            <section className={styles.section}>
              <h4 className={styles.sectionTitle}>Signal Status</h4>
              <div className={styles.dataGrid}>
                <DataRow label="Status"             value="Online"             valueColor="success" />
                <DataRow label="Active Phase"       value={selectedJunction.phase} />
                <DataRow label="Current Green Time" value={`${selectedJunction.greenTime}s`} />
              </div>
              <div className={styles.phaseBar}>
                <div
                  className={styles.phaseFill}
                  style={{ width: `${(selectedJunction.greenTime / 60) * 100}%` }}
                />
              </div>
              <p className={styles.phaseLabel}>{selectedJunction.greenTime}s of 60s cycle</p>
            </section>

            <section className={styles.aiSection}>
              <p className={styles.aiLabel}>Latest AI Recommendation (Demo Placeholder)</p>
              <p className={styles.aiText}>
                Increase green phase by +20s to reduce Northbound queue.
              </p>
              <p className={styles.aiStatus}>Status: <strong>Pending Operator Approval</strong></p>
              <Button fullWidth variant="primary" size="sm"
                onClick={() => navigate('/decision-queue')}>
                Review in Decision Queue
              </Button>
            </section>
          </>
        ) : (
          <div className={styles.emptyPanel}>
            <Search size={32} color="var(--color-border)" />
            <p>Select a junction marker on the map to view details.</p>
            {loading && <p style={{ fontSize:'var(--text-sm)', marginTop:8 }}>Loading junction data…</p>}
          </div>
        )}
      </div>
    </div>
  );
}

function DataRow({ label, value, valueColor, icon }) {
  return (
    <div className={styles.dataRow}>
      <span className={styles.dataLabel}>{label}</span>
      <span className={[styles.dataValue, valueColor === 'success' ? styles.valueSuccess : ''].join(' ')}>
        {icon && <span style={{ display: 'inline-flex', verticalAlign: 'middle', marginRight: 4 }}>{icon}</span>}
        {value}
      </span>
    </div>
  );
}
