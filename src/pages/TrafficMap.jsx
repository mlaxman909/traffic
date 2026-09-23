import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, CloudRain, Clock, WifiOff, RefreshCw } from 'lucide-react';

import Badge from '../components/Shared/Badge';
import Button from '../components/Shared/Button';
import { useApi } from '../hooks/useApi';
import { getJunctions } from '../services/api';
import styles from './TrafficMap.module.css';

// ── Helpers ──────────────────────────────────────────────────────────────────

const statusToKey = (s) => {
  if (s === 'HIGH' || s === 'CRITICAL') return 'red';
  if (s === 'MODERATE') return 'yellow';
  return 'green';
};

const severityLabel = { red: 'Congested', yellow: 'Moderate', green: 'Low Traffic' };
const severityBadge = { red: 'red', yellow: 'yellow', green: 'green' };
const STATUS_COLOR  = { red: '#ef4444', yellow: '#eab308', green: '#22c55e' };

const TOMTOM_KEY = import.meta.env.VITE_TOMTOM_API_KEY;

// Geographic centre of the 8 Vadodara junctions
const CENTER = [73.1866, 22.3076]; // [lng, lat]

// TomTom raster-tile style for MapLibre (v1 API confirmed 200 OK)
const MAP_STYLE = {
  version: 8,
  sources: {
    tomtom: {
      type: 'raster',
      tiles: [`https://api.tomtom.com/map/1/tile/basic/main/{z}/{x}/{y}.png?key=${TOMTOM_KEY}&tileSize=256&language=en-GB`],
      tileSize: 256,
      attribution: '© <a href="https://tomtom.com" target="_blank">TomTom</a>',
    },
  },
  layers: [{ id: 'tomtom-tiles', type: 'raster', source: 'tomtom' }],
};

// ── Marker DOM element factory ────────────────────────────────────────────────
function makeMarkerEl(color, isSelected) {
  const size = isSelected ? 22 : 14;
  const wrap = document.createElement('div');
  wrap.style.cssText = `width:${size}px;height:${size}px;position:relative;cursor:pointer;`;

  if (isSelected) {
    const ring = document.createElement('div');
    ring.style.cssText = `
      position:absolute;top:50%;left:50%;
      transform:translate(-50%,-50%);
      width:34px;height:34px;border-radius:50%;
      background:${color};opacity:0.28;
    `;
    wrap.appendChild(ring);
  }

  const dot = document.createElement('div');
  dot.style.cssText = `
    width:${size}px;height:${size}px;border-radius:50%;
    background:${color};border:2.5px solid #fff;
    box-shadow:0 2px 6px rgba(0,0,0,0.45);
    position:relative;z-index:1;
  `;
  wrap.appendChild(dot);
  return wrap;
}

// ── Component ────────────────────────────────────────────────────────────────
export default function TrafficMap() {
  const navigate = useNavigate();
  const mapEl    = useRef(null);
  const mapObj   = useRef(null);
  const markers  = useRef({});

  const [selected, setSelected]   = useState(null);
  const [search,   setSearch]     = useState('');
  const [filter,   setFilter]     = useState('all');
  const [mapReady, setMapReady]   = useState(false);

  const { data: raw, loading, error, refetch } = useApi(getJunctions);

  const junctions = (raw || []).map((j) => ({
    id:        j.junction_code,
    name:      j.name,
    status:    statusToKey(j.status),
    density:   j.traffic_density ?? 0,
    lat:       j.latitude,
    lng:       j.longitude,
    weather:   j.weather_condition || 'N/A',
    greenTime: j.current_green_time ?? 30,
    phase:     'N/S Green',
  }));

  const selectedJ = junctions.find((j) => j.id === selected);

  const filtered = junctions.filter((j) => {
    const matchF = filter === 'all' || j.status === filter;
    const matchS = j.id.toLowerCase().includes(search.toLowerCase()) ||
                   j.name.toLowerCase().includes(search.toLowerCase());
    return matchF && matchS;
  });
  const visibleIds = new Set(filtered.map((j) => j.id));

  // ── Init MapLibre (from CDN global window.maplibregl) ────────────────────
  useEffect(() => {
    if (!mapEl.current || mapObj.current) return;

    // Wait until CDN script has loaded window.maplibregl
    const init = () => {
      const ml = window.maplibregl;
      if (!ml) return;

      const map = new ml.Map({
        container: mapEl.current,
        style:     MAP_STYLE,
        center:    CENTER,
        zoom:      13,
        attributionControl: false,
      });

      map.addControl(new ml.NavigationControl({ showCompass: false }), 'bottom-right');
      map.addControl(new ml.AttributionControl({ compact: true }),     'bottom-right');

      map.on('load', () => setMapReady(true));
      mapObj.current = map;
    };

    if (window.maplibregl) {
      init();
    } else {
      // Poll until CDN script loads (should be fast)
      const t = setInterval(() => {
        if (window.maplibregl) { clearInterval(t); init(); }
      }, 100);
    }

    return () => {
      Object.values(markers.current).forEach((m) => m.remove());
      markers.current = {};
      mapObj.current?.remove();
      mapObj.current = null;
      setMapReady(false);
    };
  }, []);

  // ── Sync markers ──────────────────────────────────────────────────────────
  const handleSelect = useCallback((id) => setSelected((p) => (p === id ? null : id)), []);

  useEffect(() => {
    const ml  = window.maplibregl;
    const map = mapObj.current;
    if (!ml || !map || !mapReady || junctions.length === 0) return;

    junctions.forEach((j) => {
      const visible    = visibleIds.has(j.id);
      const isSelected = selected === j.id;
      const color      = STATUS_COLOR[j.status];
      const existing   = markers.current[j.id];

      // Remove if filtered out
      if (!visible) {
        existing?.remove();
        delete markers.current[j.id];
        return;
      }

      // Always rebuild so size/glow reflects selected state
      existing?.remove();
      delete markers.current[j.id];

      const el = makeMarkerEl(color, isSelected);

      const popup = new ml.Popup({
        offset: 18,
        closeButton: false,
        closeOnClick: false,
        className: 'tt-popup',
        focusAfterOpen: false,
      }).setHTML(`
        <div style="text-align:center;font-family:Inter,sans-serif;padding:4px 8px;min-width:110px">
          <strong style="display:block;font-size:13px;color:#111">${j.id}</strong>
          <span style="font-size:11px;color:#555">${j.name}</span>
        </div>
      `);

      const marker = new ml.Marker({ element: el, anchor: 'center' })
        .setLngLat([j.lng, j.lat])
        .setPopup(popup)
        .addTo(map);

      // Hover: show popup
      el.addEventListener('mouseenter', () => popup.addTo(map));
      el.addEventListener('mouseleave', () => { if (selected !== j.id) popup.remove(); });
      el.addEventListener('click', (e) => { e.stopPropagation(); handleSelect(j.id); });

      // Keep popup open for selected marker
      if (isSelected) popup.addTo(map);

      markers.current[j.id] = marker;
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapReady, junctions.length, visibleIds, selected, handleSelect]);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>

      {/* Map Area */}
      <div className={styles.mapWrapper} style={{ position: 'relative' }}>

        {/* Search / Filter Panel */}
        <div className={styles.controlPanel}
          style={{ position:'absolute', top:16, left:16, zIndex:1000,
            background:'var(--color-surface)', padding:16, borderRadius:8,
            boxShadow:'0 4px 6px rgba(0,0,0,.1)' }}>
          <div className={styles.searchWrap}>
            <Search size={15} className={styles.searchIcon} />
            <input className={styles.searchInput} placeholder="Search junction..."
              value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className={styles.filterGroup}>
            <p className={styles.filterLabel}><Filter size={12} /> Filter by status</p>
            {['all','green','yellow','red'].map((f) => (
              <button key={f}
                className={[styles.filterBtn, filter === f ? styles.filterActive : ''].join(' ')}
                onClick={() => setFilter(f)} data-status={f}>
                {f === 'all' ? 'All' : severityLabel[f]}
              </button>
            ))}
          </div>
        </div>

        {/* Error overlay */}
        {error && (
          <div style={{ position:'absolute', top:120, left:16, zIndex:1000,
            background:'var(--color-surface)', border:'1px solid var(--color-border)',
            borderRadius:8, padding:'10px 14px', display:'flex', gap:8, alignItems:'center',
            fontSize:'var(--text-sm)', color:'var(--color-text-secondary)',
            boxShadow:'0 4px 6px rgba(0,0,0,.1)' }}>
            <WifiOff size={14} color="var(--color-danger)" />
            <span>{error}</span>
            <button onClick={refetch} style={{ marginLeft:8, cursor:'pointer',
              background:'none', border:'none', color:'var(--color-primary)',
              display:'flex', alignItems:'center', gap:4 }}>
              <RefreshCw size={12} /> Retry
            </button>
          </div>
        )}

        {/* Map canvas */}
        <div ref={mapEl} className="tomtom-map" style={{ width:'100%', height:'100%' }} />

        {/* Legend */}
        <div className={styles.legend}
          style={{ position:'absolute', bottom:16, left:16, zIndex:1000,
            background:'var(--color-surface)', padding:'8px 12px', borderRadius:8,
            boxShadow:'0 2px 4px rgba(0,0,0,.1)' }}>
          {['green','yellow','red'].map((s) => (
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

      {/* Detail Panel */}
      <div className={[styles.detailPanel, selectedJ ? styles.panelOpen : ''].join(' ')}>
        {selectedJ ? (
          <>
            <div className={styles.panelHeader}>
              <div>
                <p className={styles.panelId}>{selectedJ.id}</p>
                <h2 className={styles.panelName}>{selectedJ.name}</h2>
              </div>
              <Badge variant={severityBadge[selectedJ.status]}>{severityLabel[selectedJ.status]}</Badge>
            </div>

            <section className={styles.section}>
              <h4 className={styles.sectionTitle}>Live Traffic Data — PostgreSQL</h4>
              <div className={styles.dataGrid}>
                <DataRow label="Traffic Density"  value={`${selectedJ.density}%`} />
                <DataRow label="Coordinates"
                  value={`${selectedJ.lat?.toFixed(4)}, ${selectedJ.lng?.toFixed(4)}`} />
                <DataRow label="Weather" value={selectedJ.weather} icon={<CloudRain size={13}/>} />
              </div>
            </section>

            <section className={styles.section}>
              <h4 className={styles.sectionTitle}>Signal Status</h4>
              <div className={styles.dataGrid}>
                <DataRow label="Status"             value="Online"                  valueColor="success" />
                <DataRow label="Active Phase"       value={selectedJ.phase} />
                <DataRow label="Current Green Time" value={`${selectedJ.greenTime}s`} />
              </div>
              <div className={styles.phaseBar}>
                <div className={styles.phaseFill}
                  style={{ width:`${(selectedJ.greenTime / 60) * 100}%` }} />
              </div>
              <p className={styles.phaseLabel}>{selectedJ.greenTime}s of 60s cycle</p>
            </section>

            <section className={styles.aiSection}>
              <p className={styles.aiLabel}>Latest AI Recommendation</p>
              <p className={styles.aiText}>Increase green phase by +20s to reduce Northbound queue.</p>
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
        {icon && <span style={{ display:'inline-flex', verticalAlign:'middle', marginRight:4 }}>{icon}</span>}
        {value}
      </span>
    </div>
  );
}
