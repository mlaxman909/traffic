import { useState, useCallback, useEffect, useMemo } from 'react';
import { AlertTriangle, CheckSquare, Clock, Shield, RefreshCw, AlertCircle } from 'lucide-react';
import Button from '../components/Shared/Button';
import { FormSelect } from '../components/Shared/FormInput';
import FormInput from '../components/Shared/FormInput';
import Modal from '../components/Shared/Modal';
import Badge from '../components/Shared/Badge';
import { useAuth } from '../context/AuthContext';
import { useApi } from '../hooks/useApi';
import {
  getEmergencyRoutes,
  createEmergencyRoute,
  updateEmergencyRoute,
  getJunctions,
} from '../services/api';
import styles from './EmergencyRouting.module.css';

// ── Constants & Mappings ──────────────────────────────────────────────────

const EMERGENCY_TYPES = ['Ambulance', 'Fire Service', 'Police'];
const STEPS = ['Vehicle ID', 'Route Definition', 'Route Review', 'Authorization'];

const EM_TYPE_MAP = {
  'Ambulance': 'AMBULANCE',
  'Fire Service': 'FIRE_SERVICE',
  'Police': 'POLICE',
};

const EM_TYPE_REVERSE_MAP = {
  'AMBULANCE': 'Ambulance',
  'FIRE_SERVICE': 'Fire Service',
  'POLICE': 'Police',
};

const STATUS_BADGE = {
  PLANNED: 'slate',
  ACTIVE: 'amber',
  COMPLETED: 'emerald',
  CANCELLED: 'red',
};

// ── Utility helpers ────────────────────────────────────────────────────────

function formatTime(isoString) {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleTimeString('en-IN', {
      hour: '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

function formatRouteId(id) {
  return `ER-${String(id).padStart(3, '0')}`;
}

// ── Component ─────────────────────────────────────────────────────────────

export default function EmergencyRouting() {
  const { currentUser } = useAuth();
  
  // ── State: Wizard ───────────────────────────────────────────────────────
  const [step, setStep] = useState(0);
  const [eType, setEType] = useState(EMERGENCY_TYPES[0]);
  const [vehicleId, setVehicleId] = useState('');
  const [origin, setOrigin] = useState('');
  const [dest, setDest] = useState('');
  const [confirmed, setConfirmed] = useState(false);
  const [authModal, setAuthModal] = useState(false);

  // ── State: Action & Active Route ────────────────────────────────────────
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [activeRouteId, setActiveRouteId] = useState(null);

  // ── Data Fetching ───────────────────────────────────────────────────────
  const {
    data: junctions,
    loading: juncLoading,
    error: juncError,
  } = useApi(getJunctions, []);

  const {
    data: emergencyRoutes,
    loading: routesLoading,
    error: routesError,
    refetch: refetchRoutes,
  } = useApi(getEmergencyRoutes, [{}]);

  // ── Build Lookups & Options ─────────────────────────────────────────────
  const junctionMap = useMemo(() => {
    const map = {};
    if (Array.isArray(junctions)) {
      junctions.forEach((j) => {
        map[j.id] = j;
      });
    }
    return map;
  }, [junctions]);

  const JUNCTION_OPTIONS = useMemo(() => {
    if (!Array.isArray(junctions)) return [];
    return junctions.map((j) => ({ value: j.id, label: `${j.junction_code} — ${j.name}` }));
  }, [junctions]);

  // Set defaults once junctions are loaded
  useEffect(() => {
    if (JUNCTION_OPTIONS.length > 0 && !origin && !dest) {
      setOrigin(JUNCTION_OPTIONS[0].value);
      setDest(JUNCTION_OPTIONS[Math.min(1, JUNCTION_OPTIONS.length - 1)].value);
    }
  }, [JUNCTION_OPTIONS, origin, dest]);

  const DEST_OPTIONS = JUNCTION_OPTIONS.filter((o) => String(o.value) !== String(origin));
  const ORIGIN_OPTIONS = JUNCTION_OPTIONS.filter((o) => String(o.value) !== String(dest));

  // Determine if there is an active route among the fetched data
  useEffect(() => {
    if (Array.isArray(emergencyRoutes)) {
      const active = emergencyRoutes.find((r) => r.status === 'ACTIVE');
      if (active && active.id !== activeRouteId) {
        setActiveRouteId(active.id);
      } else if (!active && activeRouteId) {
        setActiveRouteId(null);
      }
    }
  }, [emergencyRoutes, activeRouteId]);

  const activeRoute = Array.isArray(emergencyRoutes)
    ? emergencyRoutes.find((r) => r.id === activeRouteId)
    : null;

  // Derive route sequence for UI display (mock intermediate for visual only, or just origin->dest)
  const originJunc = junctionMap[origin] || { junction_code: 'Unknown', name: 'Unknown' };
  const destJunc = junctionMap[dest] || { junction_code: 'Unknown', name: 'Unknown' };
  const routeSeq = [originJunc.junction_code, destJunc.junction_code];

  // ── Actions ─────────────────────────────────────────────────────────────

  const handleActivate = async () => {
    setActionLoading(true);
    setActionError(null);

    // 1. POST new emergency route
    const createPayload = {
      emergency_type: EM_TYPE_MAP[eType] || 'AMBULANCE',
      vehicle_id: vehicleId,
      origin_junction_id: parseInt(origin, 10),
      destination_junction_id: parseInt(dest, 10),
      priority: 1,
      route_description: `${originJunc.junction_code} → ${destJunc.junction_code}`
    };

    const createRes = await createEmergencyRoute(createPayload);
    if (createRes.error) {
      setActionError(`Failed to create route: ${createRes.error}`);
      setActionLoading(false);
      return;
    }

    const newRouteId = createRes.data.id;

    // 2. PUT to authorize and activate it
    const updateRes = await updateEmergencyRoute(newRouteId, {
      authorization_status: 'AUTHORIZED',
      status: 'ACTIVE',
    });

    setActionLoading(false);

    if (updateRes.error) {
      setActionError(`Failed to activate route: ${updateRes.error}`);
      return;
    }

    setAuthModal(false);
    await refetchRoutes();
    setActiveRouteId(newRouteId);
    
    // Reset wizard
    setStep(0);
    setConfirmed(false);
    setVehicleId('');
  };

  const handleTerminate = async () => {
    if (!activeRouteId) return;
    setActionLoading(true);
    setActionError(null);

    const { error } = await updateEmergencyRoute(activeRouteId, {
      status: 'COMPLETED',
    });

    setActionLoading(false);

    if (error) {
      setActionError(`Failed to terminate route: ${error}`);
      return;
    }

    await refetchRoutes();
    setActiveRouteId(null);
  };

  // ── Render Helpers ──────────────────────────────────────────────────────

  if (juncLoading || routesLoading) {
    return (
      <div className={styles.page}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', color: 'var(--color-text-secondary)', gap: 'var(--space-3)' }}>
          <RefreshCw size={32} className="spinIcon" />
          <p>Loading emergency routes...</p>
        </div>
      </div>
    );
  }

  if (juncError || routesError) {
    return (
      <div className={styles.page}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%', color: 'var(--color-text-secondary)', gap: 'var(--space-3)' }}>
          <AlertCircle size={32} color="var(--color-danger)" />
          <p style={{ color: 'var(--color-text-primary)' }}>Unable to load emergency routes. Please try again.</p>
          <Button variant="secondary" icon={RefreshCw} onClick={refetchRoutes}>Retry</Button>
        </div>
      </div>
    );
  }

  // Active Route View
  if (activeRoute) {
    const actOrigin = junctionMap[activeRoute.origin_junction_id]?.junction_code || 'Origin';
    const actDest = junctionMap[activeRoute.destination_junction_id]?.junction_code || 'Dest';
    const actRouteSeq = [actOrigin, actDest];
    const displayEType = EM_TYPE_REVERSE_MAP[activeRoute.emergency_type] || activeRoute.emergency_type;

    return (
      <div className={styles.activePage}>
        <div className={styles.activeCard}>
          {actionError && (
            <div style={{ background: '#fef2f2', border: '1px solid #dc2626', color: '#dc2626', padding: '12px', borderRadius: '4px', fontSize: '14px' }}>
              {actionError}
            </div>
          )}
          <div className={styles.activeHeader}>
            <AlertTriangle size={24} color="var(--color-warning)" />
            <h2>Active Green Corridor — {displayEType} {activeRoute.vehicle_id}</h2>
            <Badge variant="amber">ACTIVE</Badge>
          </div>
          <p className={styles.activeSub}>
            Route: {activeRoute.route_description || actRouteSeq.join(' → ')} &nbsp;|&nbsp; Authorized by: Operator {activeRoute.created_by || 'System'}
          </p>
          <div className={styles.progressTrack}>
            {actRouteSeq.map((j, i) => (
              <div key={j} className={styles.progressStep}>
                <div className={[styles.progressDot, i === 0 ? styles.progressDone : ''].join(' ')} />
                <span>{j}</span>
                {i < actRouteSeq.length - 1 && <div className={styles.progressLine} />}
              </div>
            ))}
          </div>
          <Button variant="danger" disabled={actionLoading} onClick={handleTerminate}>
            {actionLoading ? 'Terminating...' : 'Terminate Corridor & Resume Normal Operations'}
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      {/* Left: Wizard */}
      <div className={styles.wizard}>
        {/* Operator Badge */}
        <div className={styles.opBadge}>
          <Shield size={14} />
          <span>Session: Operator {currentUser?.name || 'Unknown'} — All actions are logged</span>
        </div>

        {/* Stepper */}
        <div className={styles.stepper}>
          {STEPS.map((s, i) => (
            <div key={s} className={styles.stepperItem}>
              <div className={[
                styles.stepBubble,
                i < step ? styles.stepDone : i === step ? styles.stepActive : styles.stepPending,
              ].join(' ')}>
                {i < step ? <CheckSquare size={14} /> : i + 1}
              </div>
              <span className={[styles.stepLabel, i === step ? styles.stepLabelActive : ''].join(' ')}>{s}</span>
              {i < STEPS.length - 1 && <div className={styles.stepConnector} />}
            </div>
          ))}
        </div>

        {/* Action Error */}
        {actionError && (
          <div style={{ background: '#fef2f2', border: '1px solid #dc2626', color: '#dc2626', padding: '12px', borderRadius: '4px', fontSize: '14px' }}>
            {actionError}
          </div>
        )}

        {/* Step panels */}
        <div className={styles.stepPanel}>
          {step === 0 && (
            <div className={styles.stepContent}>
              <h3 className={styles.stepTitle}>Step 1: Vehicle Identification</h3>
              <FormSelect id="eType" label="Emergency Type" value={eType}
                onChange={(e) => setEType(e.target.value)} options={EMERGENCY_TYPES} />
              <FormInput id="vehicleId" label="Vehicle ID / Callsign" placeholder="e.g. AMB-07, FIRE-E12"
                value={vehicleId} onChange={(e) => setVehicleId(e.target.value)} />
              <Button variant="primary" fullWidth disabled={!vehicleId.trim()}
                onClick={() => setStep(1)}>Continue</Button>
            </div>
          )}

          {step === 1 && (
            <div className={styles.stepContent}>
              <h3 className={styles.stepTitle}>Step 2: Route Definition</h3>
              <FormSelect id="origin" label="Starting Junction" value={origin}
                onChange={(e) => setOrigin(e.target.value)} options={ORIGIN_OPTIONS} />
              <FormSelect id="dest"   label="Destination Junction" value={dest}
                onChange={(e) => setDest(e.target.value)} options={DEST_OPTIONS} />
              <div className={styles.navRow}>
                <Button variant="secondary" onClick={() => setStep(0)}>Back</Button>
                <Button variant="primary" disabled={!origin || !dest} onClick={() => setStep(2)}>Calculate Route</Button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className={styles.stepContent}>
              <h3 className={styles.stepTitle}>Step 3: Route Review & Impact</h3>
              <div className={styles.alertBox}>
                <AlertTriangle size={16} />
                <p>This route will <strong>temporarily override</strong> normal signal operations across {routeSeq.length} junctions. Cross-traffic will experience delays of up to 2 minutes.</p>
              </div>
              <div className={styles.routeSummary}>
                <div className={styles.dataRow}><span>Vehicle:</span><strong>{eType} — {vehicleId}</strong></div>
                <div className={styles.dataRow}><span>Junction Sequence:</span><strong>{routeSeq.join(' → ')}</strong></div>
                <div className={styles.dataRow}><span>Current Route Traffic:</span><Badge variant="yellow">Moderate</Badge></div>
                <div className={styles.dataRow}><span>Est. Corridor Status:</span><span style={{ color: 'var(--color-success)' }}>Clear Path Available</span></div>
              </div>
              <div className={styles.navRow}>
                <Button variant="secondary" onClick={() => setStep(1)}>Back</Button>
                <Button variant="primary" onClick={() => setStep(3)}>Proceed to Authorization</Button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className={styles.stepContent}>
              <h3 className={styles.stepTitle}>Step 4: Authorization</h3>
              <label className={styles.confirmCheck}>
                <input type="checkbox" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
                <span>I confirm this is a <strong>verified emergency</strong> requiring a green-wave corridor override. This action will be permanently logged.</span>
              </label>
              <div className={styles.navRow}>
                <Button variant="secondary" onClick={() => setStep(2)}>Back</Button>
                <Button
                  variant="danger"
                  fullWidth
                  disabled={!confirmed}
                  onClick={() => { setActionError(null); setAuthModal(true); }}
                >
                  Simulate Green Corridor (Prototype)
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right: Map Preview + History */}
      <div className={styles.rightPanel}>
        {/* Route Preview */}
        <div className={styles.previewCard}>
          <h4 className={styles.previewTitle}>Green Corridor Preview (Prototype)</h4>
          <svg className={styles.previewSvg} viewBox="0 0 100 60">
            <line x1="15" y1="30" x2="85" y2="30" stroke="#e2e8f0" strokeWidth="4" />
            <line x1="15" y1="30" x2="85" y2="30" stroke="#22c55e" strokeWidth="2.5" strokeDasharray="4 2" />
            {routeSeq.map((j, i) => {
              const x = 15 + i * 70;
              return (
                <g key={`${j}-${i}`}>
                  <circle cx={x} cy={30} r={4} fill="#22c55e" stroke="#fff" strokeWidth="1" />
                  <text x={x} y={42} textAnchor="middle" fontSize="5" fill="var(--color-text-primary)" fontFamily="Inter">{j}</text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Emergency History */}
        <div className={styles.historyCard}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
            <h4 className={styles.previewTitle} style={{ margin: 0 }}><Clock size={14} /> Emergency Corridor Audit Log</h4>
            <button
              onClick={refetchRoutes}
              title="Refresh History"
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-secondary)' }}
            >
              <RefreshCw size={14} />
            </button>
          </div>
          <div style={{ overflowY: 'auto', flex: 1 }}>
            {(!emergencyRoutes || emergencyRoutes.length === 0) ? (
              <div style={{ textAlign: 'center', padding: 'var(--space-5)', color: 'var(--color-text-secondary)', fontSize: 'var(--text-sm)' }}>
                No emergency routes available.
              </div>
            ) : (
              <table className={styles.histTable}>
                <thead>
                  <tr>
                    <th>ID</th><th>Time</th><th>Type</th><th>Vehicle</th><th>Route</th><th>Operator</th><th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {emergencyRoutes.map((h) => {
                    const statusStr = h.status.toUpperCase();
                    const badgeVar = STATUS_BADGE[statusStr] || 'slate';
                    const dispType = EM_TYPE_REVERSE_MAP[h.emergency_type] || h.emergency_type;
                    const rDesc = h.route_description || `${junctionMap[h.origin_junction_id]?.junction_code || h.origin_junction_id} → ${junctionMap[h.destination_junction_id]?.junction_code || h.destination_junction_id}`;
                    
                    return (
                      <tr key={h.id}>
                        <td className={styles.mono}>{formatRouteId(h.id)}</td>
                        <td>{formatTime(h.created_at)}</td>
                        <td>{dispType}</td>
                        <td className={styles.mono}>{h.vehicle_id}</td>
                        <td>{rDesc}</td>
                        <td className={styles.mono}>{h.created_by ? `OP-${h.created_by}` : 'System'}</td>
                        <td><Badge variant={badgeVar}>{h.status}</Badge></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Auth Modal */}
      <Modal isOpen={authModal} onClose={() => !actionLoading && setAuthModal(false)} title="Final Authorization Confirmation" variant="danger" size="md"
        footer={
          <>
            <Button variant="secondary" disabled={actionLoading} onClick={() => setAuthModal(false)}>Cancel</Button>
            <Button variant="danger" disabled={actionLoading} onClick={handleActivate}>
              {actionLoading ? 'Activating...' : 'Activate Corridor'}
            </Button>
          </>
        }
      >
        <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6, marginBottom: 'var(--space-3)' }}>
          You are authorizing a <strong>Green Wave Corridor</strong> for <strong>{eType} — {vehicleId}</strong>.
        </p>
        <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6, marginBottom: 'var(--space-3)' }}>
          Route: <strong>{routeSeq.join(' → ')}</strong>
        </p>
        <div style={{ fontSize: 'var(--text-xs)', padding: 'var(--space-3)', background: 'var(--color-surface-hover)', borderRadius: 'var(--radius-sm)', color: 'var(--color-text-secondary)' }}>
          Note: In Phase 1 prototype, this simulates the authorization workflow. Physical traffic hardware integration is out of scope.
        </div>
      </Modal>
    </div>
  );
}
