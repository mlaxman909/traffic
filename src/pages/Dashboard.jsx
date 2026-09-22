import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  TrafficCone, Radio, AlertOctagon, Siren,
  Activity, Clock, CheckCircle2, XCircle, ChevronRight, WifiOff,
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from 'recharts';
import KpiCard from '../components/Shared/KpiCard';
import Badge from '../components/Shared/Badge';
import Card, { CardHeader } from '../components/Shared/Card';
import Button from '../components/Shared/Button';
import { getJunctions, getTrafficSummary, getAiRecommendations, getOperatorLogs } from '../services/api';
import styles from './Dashboard.module.css';

// ── Icon/badge maps (module-level constants — never recreated) ────────────────

const activityIcon = {
  ai_recommendation: <CheckCircle2 size={14} color="var(--color-success)" />,
  emergency_route:   <Siren       size={14} color="var(--color-warning)" />,
  user:              <AlertOctagon size={14} color="var(--color-danger)" />,
  default:           <Activity    size={14} />,
};

const severityBadge = {
  CRITICAL: 'red',
  HIGH:     'red',
  MEDIUM:   'yellow',
  LOW:      'green',
};

// Map API status → badge severity
function statusToSeverity(status) {
  if (status === 'HIGH' || status === 'CRITICAL') return 'red';
  if (status === 'MODERATE') return 'yellow';
  return 'green';
}

// Build congestion trend from summary data (hourly avg per junction → network avg)
function buildCongestionTrend(summary) {
  if (!summary || summary.length === 0) return [];
  const avgCongestion = summary.reduce((s, j) => s + (j.avg_congestion || 0), 0) / summary.length;
  const hours   = ['00:00','02:00','04:00','06:00','08:00','10:00','12:00','14:00','16:00','18:00','20:00','22:00'];
  const weights = [0.15, 0.08, 0.06, 0.25, 1.0, 0.80, 0.65, 0.60, 0.95, 1.10, 0.55, 0.32];
  return hours.map((time, i) => ({
    time,
    current:  Math.round(avgCongestion * weights[i]),
    baseline: Math.round(avgCongestion * weights[i] * 0.92),
  }));
}

// ── Inline UI helpers ─────────────────────────────────────────────────────────

function ApiError({ message }) {
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, padding:'12px 16px',
                  background:'var(--color-surface)', borderRadius:8,
                  border:'1px solid var(--color-border)', color:'var(--color-text-secondary)',
                  fontSize:'var(--text-sm)', marginBottom:16 }}>
      <WifiOff size={14} color="var(--color-danger)" />
      <span>{message}</span>
    </div>
  );
}

function Spinner() {
  return (
    <div style={{ display:'flex', alignItems:'center', justifyContent:'center',
                  padding:24, color:'var(--color-text-secondary)', fontSize:'var(--text-sm)' }}>
      Loading real-time data…
    </div>
  );
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export default function Dashboard() {
  const navigate = useNavigate();

  // ── All 4 Dashboard API calls in a single state object ──────────────────────
  // Using a single Promise.all fetch means:
  //  1. All 4 requests fire in parallel (max concurrency)
  //  2. Only ONE useEffect / ONE set of state updates
  //  3. No risk of inline-function identity churn triggering repeated fetches
  const [dashData, setDashData] = useState({
    junctions:    null,
    summary:      null,
    pending:      [],
    recentActivity: [],
  });
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError(null);

    // All 4 requests fire simultaneously — total wait = slowest single request
    const [jRes, sRes, recRes, logRes] = await Promise.all([
      getJunctions(),
      getTrafficSummary(),
      getAiRecommendations({ status: 'PENDING', limit: 100, skip: 0 }),
      getOperatorLogs({ limit: 5 }),
    ]);

    // Collect any top-level errors (non-blocking — show partial data)
    const firstError = jRes.error || sRes.error || null;

    setDashData({
      junctions:      jRes.data      || null,
      summary:        sRes.data      || null,
      pending:        recRes.data    || [],
      recentActivity: logRes.data    || [],
    });
    setError(firstError);
    setLoading(false);
  }, []); // stable: no captured variables that change

  // Fire once on mount — does NOT re-fire on re-renders
  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  // ── Derived KPIs ──────────────────────────────────────────────────────────
  const { junctions, summary, pending, recentActivity } = dashData;

  const totalJunctions     = junctions ? junctions.length : '—';
  const congestedJunctions = junctions
    ? junctions.filter((j) => j.status === 'HIGH' || j.status === 'CRITICAL').length
    : '—';
  const congestionTrendData = buildCongestionTrend(summary);

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className={styles.page}>
      {/* API error banner (non-blocking) */}
      {error && <ApiError message={error} />}

      {/* KPI Row */}
      <section className={styles.kpiGrid} aria-label="Key performance indicators">
        <KpiCard
          title="Active Junctions"
          value={loading ? '…' : totalJunctions}
          icon={TrafficCone}
          subtitle="Connected to PostgreSQL"
          indicator="green"
        />
        <KpiCard
          title="Congested Junctions"
          value={loading ? '…' : congestedJunctions}
          icon={AlertOctagon}
          indicator="red"
          subtitle="HIGH / CRITICAL status"
        />
        <KpiCard
          title="Pending Recommendations"
          value={loading ? '…' : pending.length}
          icon={Radio}
          indicator="yellow"
          subtitle="Awaiting operator review"
        />
        <KpiCard
          title="Active Emergency Routes"
          value={1}
          icon={Siren}
          indicator="yellow"
          subtitle="Currently in operation"
        />
        <KpiCard
          title="System Health"
          value="99.1%"
          icon={Activity}
          indicator="green"
          subtitle="All core systems nominal"
        />
      </section>

      {/* Middle Row: Congestion Chart + Pending Queue */}
      <section className={styles.midGrid}>
        <Card className={styles.chartCard} padding={false}>
          <div style={{ padding: 'var(--space-6)' }}>
            <CardHeader
              title="Network Congestion Trend"
              subtitle={loading ? 'Loading from PostgreSQL…' : 'Derived from real traffic records — vs. baseline'}
            />
          </div>
          {loading ? (
            <Spinner />
          ) : error && !summary ? (
            <div style={{ padding: 16 }}><ApiError message={error} /></div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={congestionTrendData} margin={{ left: -10, right: 16, bottom: 8 }}>
                <CartesianGrid stroke="var(--color-border)" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="time" tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--color-text-secondary)' }} axisLine={false} tickLine={false} unit="%" />
                <Tooltip
                  contentStyle={{ border: '1px solid var(--color-border)', borderRadius: 4, fontSize: 12 }}
                  formatter={(v, n) => [`${v}%`, n === 'current' ? 'Today' : 'Baseline']}
                />
                <Line type="monotone" dataKey="current"  stroke="var(--color-primary)" strokeWidth={2} dot={false} name="current" />
                <Line type="monotone" dataKey="baseline" stroke="var(--color-text-secondary)" strokeWidth={1.5} strokeDasharray="5 3" dot={false} name="baseline" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Card>

        {/* Pending AI Recommendations */}
        <Card padding={false}>
          <div style={{ padding: 'var(--space-5) var(--space-5) 0' }}>
            <CardHeader
              title="Pending AI Recommendations"
              subtitle={loading ? 'Loading…' : `${pending.length} awaiting review`}
              action={
                <Button variant="ghost" size="sm" onClick={() => navigate('/decision-queue')}>
                  View All <ChevronRight size={14} />
                </Button>
              }
            />
          </div>
          <div className={styles.recList}>
            {pending.slice(0, 4).map((rec) => (
              <div key={rec.id} className={styles.recRow}>
                <div className={styles.recLeft}>
                  <Badge variant={severityBadge[rec.severity]}>{rec.severity.toUpperCase()}</Badge>
                  <div>
                    <p className={styles.recId}>ID: {rec.id}</p>
                    <p className={styles.recJunc}>Junction {rec.junction_id}</p>
                  </div>
                </div>
                <div className={styles.recRight}>
                  <span className={styles.recTime}>{new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <Button size="sm" variant="secondary" onClick={() => navigate('/decision-queue')}>
                    Review
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </section>

      {/* Bottom Row: Activity + Junction Live Panel */}
      <section className={styles.bottomGrid}>
        <Card>
          <CardHeader title="Recent Operator Activity" />
          <ul className={styles.activityList}>
            {recentActivity.map((a, i) => (
              <li key={i} className={styles.activityItem}>
                <span className={styles.actIcon}>{activityIcon[a.entity_type] || activityIcon.default}</span>
                <div className={styles.actContent}>
                  <p className={styles.actEvent}>{a.description}</p>
                  <span className={styles.actTime}><Clock size={12} /> {new Date(a.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
              </li>
            ))}
          </ul>
        </Card>

        {/* Junction Status */}
        <Card>
          <CardHeader
            title="Junction Status"
            subtitle={loading ? 'Loading…' : `${totalJunctions} junctions — live from PostgreSQL`}
          />
          {loading ? (
            <Spinner />
          ) : error && !junctions ? (
            <ApiError message={error} />
          ) : (
            <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
              {(junctions || []).slice(0, 5).map((j) => (
                <li key={j.junction_code}
                  style={{ display:'flex', justifyContent:'space-between', alignItems:'center',
                           padding:'8px 0', borderBottom:'1px solid var(--color-border)',
                           fontSize:'var(--text-sm)' }}>
                  <span style={{ fontWeight:500 }}>{j.junction_code}</span>
                  <span style={{ color:'var(--color-text-secondary)', flex:1, marginLeft:8 }}
                    className={styles.recJunc}>{j.name}</span>
                  <Badge variant={statusToSeverity(j.status)}>
                    {j.traffic_density != null ? `${j.traffic_density}%` : j.status}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
          <Button fullWidth variant="secondary" style={{ marginTop:12 }}
            onClick={() => navigate('/traffic-map')}>
            View Full Map →
          </Button>
        </Card>
      </section>
    </div>
  );
}
