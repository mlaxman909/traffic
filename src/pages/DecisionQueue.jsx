/**
 * src/pages/DecisionQueue.jsx
 * ============================
 * Decision Queue — connected to real PostgreSQL database via FastAPI.
 *
 * Data source: GET /api/ai-recommendations  (real DB, not mockData.js)
 * Actions:     PUT /api/ai-recommendations/{id}  (approve / reject)
 *
 * Field mapping (API → UI):
 *   id                   → display as "REC-{id}"
 *   junction_id          → looked up from /api/junctions junction list
 *   recommendation_text  → suggestedAction (main action card text)
 *   reason               → analysis text
 *   severity             → 'CRITICAL'|'HIGH'|'MEDIUM'|'LOW' → badge color
 *   status               → 'PENDING'|'APPROVED'|'REJECTED' → tab routing
 *   current_green_time   → current green time display
 *   suggested_green_time → suggested green time display
 *   created_at           → formatted time display
 *   reviewed_at          → shown in approved/rejected view
 *   rejection_reason     → shown in rejected view
 *
 * Fields NOT in API (no mock fallback used):
 *   currentDensity, vehicleCount, expectedImpact → shown as N/A
 *
 * Phase 4 note:
 *   reviewed_by is currently hardcoded to user id=1 (J. Sharma) because
 *   JWT authentication is not yet implemented. Replace with the logged-in
 *   user's database ID once auth is in place.
 */

import { useState, useCallback } from 'react';
import { CheckCircle2, XCircle, Inbox, ArrowRight, RefreshCw, AlertCircle, Activity } from 'lucide-react';
import Badge from '../components/Shared/Badge';
import Button from '../components/Shared/Button';
import Modal from '../components/Shared/Modal';
import { useApi } from '../hooks/useApi';
import {
  getAiRecommendations,
  updateAiRecommendation,
  getJunctions,
  generateAiRecommendations,
} from '../services/api';
import styles from './DecisionQueue.module.css';

// ── Constants ────────────────────────────────────────────────────────────────

/**
 * Map API severity values (uppercase) to Badge variant colors.
 * API returns: CRITICAL | HIGH | MEDIUM | LOW
 * Badge accepts: red | yellow | green
 */
const SEVERITY_BADGE = {
  CRITICAL: 'red',
  HIGH:     'red',
  MEDIUM:   'yellow',
  LOW:      'green',
};

/**
 * Map API status values (uppercase) to Badge variant colors.
 * API returns: PENDING | APPROVED | REJECTED
 */
const STATUS_BADGE = {
  PENDING:  'amber',
  APPROVED: 'emerald',
  REJECTED: 'slate',
};

/** Tabs match the lowercase version of API status values. */
const TABS = ['pending', 'approved', 'rejected'];

/** Pre-defined rejection reasons shown in the modal radio list. */
const REJECT_REASONS = [
  'Unsafe conditions at junction',
  'Inaccurate traffic data',
  'Prioritizing another route',
  'Insufficient justification',
  'Other',
];

// ── Utility helpers ───────────────────────────────────────────────────────────

/**
 * Format an ISO 8601 datetime string from the API into a short time display.
 * e.g. "2026-08-28T12:45:28.623429+05:30" → "12:45 PM"
 */
function formatTime(isoString) {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleTimeString('en-IN', {
      hour:   '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

/**
 * Format an ISO 8601 datetime string to a full readable date+time.
 * e.g. "2026-08-28T12:45:28.623429+05:30" → "28 Aug 2026, 12:45 PM"
 */
function formatDateTime(isoString) {
  if (!isoString) return '—';
  try {
    return new Date(isoString).toLocaleString('en-IN', {
      day:    '2-digit',
      month:  'short',
      year:   'numeric',
      hour:   '2-digit',
      minute: '2-digit',
    });
  } catch {
    return isoString;
  }
}

/**
 * Build a display ID from the numeric database primary key.
 * e.g. 1 → "REC-001"
 */
function formatRecId(numericId) {
  return `REC-${String(numericId).padStart(3, '0')}`;
}

// ── Component ────────────────────────────────────────────────────────────────

export default function DecisionQueue() {
  // ── Tab and selection state ──────────────────────────────────────────────
  const [tab, setTab]     = useState('pending');
  const [selected, setSelected] = useState(null);

  // ── Modal state ──────────────────────────────────────────────────────────
  const [approveModal, setApproveModal] = useState(false);
  const [rejectModal, setRejectModal]   = useState(false);
  const [rejectReason, setRejectReason] = useState(REJECT_REASONS[0]);
  const [rejectNote, setRejectNote]     = useState('');

  // ── Action in-progress state (prevents double-submit) ───────────────────
  const [actionLoading, setActionLoading] = useState(false);
  const [actionError, setActionError]     = useState(null);
  
  const [generating, setGenerating]       = useState(false);

  // ── Fetch recommendations from real API ──────────────────────────────────
  const {
    data: recommendations,
    loading: recsLoading,
    error: recsError,
    refetch: refetchRecs,
  } = useApi(getAiRecommendations, [{}]);

  // ── Fetch junctions list to resolve junction_id → name ──────────────────
  // This is a small list (8 rows) — safe to fetch once and keep in memory.
  const {
    data: junctions,
  } = useApi(getJunctions, []);

  // ── Build a junction lookup map: { 1: { junction_code, name, ... } } ────
  const junctionMap = {};
  if (Array.isArray(junctions)) {
    junctions.forEach((j) => { junctionMap[j.id] = j; });
  }

  // ── Helper: resolve junction display from a recommendation ────────────────
  function resolveJunction(rec) {
    const j = junctionMap[rec.junction_id];
    if (!j) return { code: `J-${rec.junction_id}`, name: `Junction ${rec.junction_id}` };
    return { code: j.junction_code, name: j.name };
  }

  // ── Filter recommendations by the active tab ─────────────────────────────
  const allRecs    = Array.isArray(recommendations) ? recommendations : [];
  const filtered   = allRecs.filter((r) => r.status.toLowerCase() === tab);
  const selectedRec = allRecs.find((r) => r.id === selected) ?? null;

  // ── Tab click — switch tab, auto-select first item in new tab ────────────
  function handleTabClick(newTab) {
    setTab(newTab);
    setActionError(null);
    const first = allRecs.find((r) => r.status.toLowerCase() === newTab);
    setSelected(first?.id ?? null);
  }

  // ── Approve action ───────────────────────────────────────────────────────
  const handleApprove = useCallback(async () => {
    if (!selectedRec) return;
    setActionLoading(true);
    setActionError(null);

    const { error } = await updateAiRecommendation(selectedRec.id, {
      status:      'APPROVED',
    });

    setActionLoading(false);

    if (error) {
      setActionError(`Approval failed: ${error}`);
      return;
    }

    setApproveModal(false);
    await refetchRecs();

    // Move selection to next pending item after approval
    const nextPending = allRecs.find(
      (r) => r.id !== selectedRec.id && r.status === 'PENDING'
    );
    setSelected(nextPending?.id ?? null);
  }, [selectedRec, allRecs, refetchRecs]);

  // ── Reject action ────────────────────────────────────────────────────────
  const handleReject = useCallback(async () => {
    if (!selectedRec) return;
    setActionLoading(true);
    setActionError(null);

    // Build rejection_reason combining radio choice and optional note
    const fullReason = rejectNote.trim()
      ? `${rejectReason} — ${rejectNote.trim()}`
      : rejectReason;

    const { error } = await updateAiRecommendation(selectedRec.id, {
      status:           'REJECTED',
      rejection_reason: fullReason,
    });

    setActionLoading(false);

    if (error) {
      setActionError(`Rejection failed: ${error}`);
      return;
    }

    setRejectModal(false);
    setRejectNote('');
    await refetchRecs();

    // Move selection to next pending item after rejection
    const nextPending = allRecs.find(
      (r) => r.id !== selectedRec.id && r.status === 'PENDING'
    );
    setSelected(nextPending?.id ?? null);
  }, [selectedRec, allRecs, rejectReason, rejectNote, refetchRecs]);

  // ── Generate AI Recommendations ───────────────────────────────────────────
  const handleGenerate = useCallback(async () => {
    setGenerating(true);
    setActionError(null);
    const { error } = await generateAiRecommendations();
    setGenerating(false);
    if (error) {
      setActionError(`Generation failed: ${error}`);
    } else {
      await refetchRecs();
      setTab('pending');
    }
  }, [refetchRecs]);

  // ── Render helpers ───────────────────────────────────────────────────────

  /** Loading state — shown while initial fetch is in progress */
  if (recsLoading) {
    return (
      <div className={styles.page}>
        <div className={styles.emptyDetail} style={{ height: '60vh' }}>
          <RefreshCw size={32} color="var(--color-text-secondary)" className={styles.spinIcon} />
          <p>Loading recommendations…</p>
        </div>
      </div>
    );
  }

  /** Error state — shown when the API request fails entirely */
  if (recsError) {
    return (
      <div className={styles.page}>
        <div className={styles.emptyDetail} style={{ height: '60vh' }}>
          <AlertCircle size={32} color="var(--color-danger, #dc2626)" />
          <p style={{ color: 'var(--color-text-primary)' }}>
            Unable to load recommendations.
          </p>
          <p style={{ fontSize: 'var(--text-xs)', color: 'var(--color-text-secondary)', maxWidth: 380, textAlign: 'center' }}>
            {recsError}
          </p>
          <Button variant="secondary" icon={RefreshCw} onClick={refetchRecs}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  // ── Main render ───────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>

      {/* ── Tabs ─────────────────────────────────────────────────────────── */}
      <div className={styles.tabs}>
        {TABS.map((t) => {
          const count = allRecs.filter((r) => r.status.toLowerCase() === t).length;
          return (
            <button
              key={t}
              className={[styles.tab, tab === t ? styles.tabActive : ''].join(' ')}
              onClick={() => handleTabClick(t)}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
              <span className={[styles.tabCount, tab === t ? styles.tabCountActive : ''].join(' ')}>
                {count}
              </span>
            </button>
          );
        })}

        {/* Generate AI Recommendations */}
        <Button
          variant="secondary"
          size="sm"
          style={{ marginLeft: 'auto', marginRight: '8px' }}
          onClick={handleGenerate}
          disabled={generating}
        >
          <Activity size={14} style={{ marginRight: 6 }} />
          {generating ? 'Analyzing Traffic...' : 'Generate AI Recommendations'}
        </Button>

        {/* Refresh button — manually triggers a re-fetch from the API */}
        <button
          className={styles.tab}
          onClick={refetchRecs}
          title="Refresh recommendations from database"
        >
          <RefreshCw size={14} />
        </button>
      </div>

      {/* ── Action-level error banner (approve/reject failed) ────────────── */}
      {actionError && (
        <div
          style={{
            background: 'var(--color-danger-subtle, #fef2f2)',
            border:     '1px solid var(--color-danger, #dc2626)',
            borderRadius: 'var(--radius-md)',
            padding: 'var(--space-3) var(--space-4)',
            fontSize: 'var(--text-sm)',
            color: 'var(--color-danger, #dc2626)',
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-2)',
          }}
        >
          <AlertCircle size={16} />
          {actionError}
        </div>
      )}

      {/* ── Split pane: master list + detail ─────────────────────────────── */}
      <div className={styles.splitPane}>

        {/* ── Master list ──────────────────────────────────────────────── */}
        <div className={styles.masterList}>
          {filtered.length === 0 ? (
            <div className={styles.empty}>
              <Inbox size={32} color="var(--color-border)" />
              <p>No {tab} recommendations.</p>
            </div>
          ) : (
            filtered.map((rec) => {
              const junc = resolveJunction(rec);
              const severityKey = rec.severity?.toUpperCase() ?? 'MEDIUM';
              return (
                <button
                  key={rec.id}
                  className={[styles.recCard, selected === rec.id ? styles.recCardActive : ''].join(' ')}
                  onClick={() => { setSelected(rec.id); setActionError(null); }}
                >
                  <div className={styles.recCardTop}>
                    <Badge variant={SEVERITY_BADGE[severityKey] ?? 'yellow'}>
                      {severityKey}
                    </Badge>
                    <span className={styles.recTime}>{formatTime(rec.created_at)}</span>
                  </div>
                  <p className={styles.recId}>{formatRecId(rec.id)}</p>
                  <p className={styles.recJunc}>{junc.name}</p>
                  <p className={styles.recSnippet}>{rec.recommendation_text}</p>
                </button>
              );
            })
          )}
        </div>

        {/* ── Detail pane ──────────────────────────────────────────────── */}
        <div className={styles.detailPane}>
          {selectedRec && selectedRec.status.toLowerCase() === tab ? (
            (() => {
              const junc       = resolveJunction(selectedRec);
              const statusKey  = selectedRec.status?.toUpperCase() ?? 'PENDING';
              const severityKey = selectedRec.severity?.toUpperCase() ?? 'MEDIUM';
              return (
                <>
                  {/* ── Detail header ──────────────────────────────────── */}
                  <div className={styles.detailHeader}>
                    <div>
                      <p className={styles.detailId}>
                        Decision ID: <strong>{formatRecId(selectedRec.id)}</strong>
                      </p>
                      <p className={styles.detailTime}>
                        Created: {formatDateTime(selectedRec.created_at)}
                      </p>
                    </div>
                    <Badge variant={STATUS_BADGE[statusKey] ?? 'amber'}>
                      {selectedRec.status}
                    </Badge>
                  </div>

                  {/* ── Current State ──────────────────────────────────── */}
                  <section className={styles.section}>
                    <h3 className={styles.sectionTitle}>Current State</h3>
                    <div className={styles.dataGrid}>
                      <DataItem
                        label="Junction"
                        value={`${junc.name} (${junc.code})`}
                      />
                      <DataItem
                        label="Congestion Severity"
                        value={
                          <Badge variant={SEVERITY_BADGE[severityKey] ?? 'yellow'}>
                            {severityKey}
                          </Badge>
                        }
                      />
                      <DataItem
                        label="Current Green Time"
                        value={selectedRec.current_green_time != null
                          ? `${selectedRec.current_green_time}s`
                          : '—'}
                        mono
                      />
                      <DataItem
                        label="Suggested Green Time"
                        value={selectedRec.suggested_green_time != null
                          ? `${selectedRec.suggested_green_time}s`
                          : '—'}
                        mono
                      />
                      {/* Vehicle count / density: not in API — shown as N/A */}
                      <DataItem label="Vehicle Count"   value="N/A" mono />
                      <DataItem label="Traffic Density" value="N/A" mono />
                    </div>
                  </section>

                  {/* ── AI Analysis & Suggestion ────────────────────────── */}
                  <section className={[styles.section, styles.aiSection].join(' ')}>
                    <h3 className={styles.sectionTitle}>SignalAI Analysis & Suggestion</h3>
                    <div className={styles.explainer}>
                      <p>
                        <strong>Analysis:</strong>{' '}
                        {selectedRec.reason || '—'}
                      </p>
                      <p>
                        <strong>Suggested Action:</strong>{' '}
                        {selectedRec.recommendation_text}
                      </p>
                      {selectedRec.suggested_green_time != null && (
                        <p>
                          <strong>Suggested Green Time:</strong>{' '}
                          <span className={styles.mono}>{selectedRec.suggested_green_time}s</span>
                          {selectedRec.current_green_time != null && (
                            <> (currently {selectedRec.current_green_time}s)</>
                          )}
                        </p>
                      )}
                      {/* Expected impact: not in DB — noted as unavailable */}
                      <p style={{ color: 'var(--color-text-secondary)', fontStyle: 'italic', fontSize: 'var(--text-xs)' }}>
                        Expected impact data will be available once the AI engine is integrated (Phase 4).
                      </p>
                    </div>
                  </section>

                  {/* ── Review info (approved / rejected) ───────────────── */}
                  {selectedRec.status !== 'PENDING' && (
                    <section className={styles.section}>
                      <h3 className={styles.sectionTitle}>Review Information</h3>
                      <div className={styles.dataGrid}>
                        <DataItem
                          label="Reviewed At"
                          value={formatDateTime(selectedRec.reviewed_at)}
                        />
                        {selectedRec.rejection_reason && (
                          <DataItem
                            label="Rejection Reason"
                            value={selectedRec.rejection_reason}
                          />
                        )}
                      </div>
                    </section>
                  )}

                  {/* ── Action bar — only for PENDING recommendations ───── */}
                  {selectedRec.status === 'PENDING' && (
                    <div className={styles.actionBar}>
                      <Button
                        variant="danger"
                        icon={XCircle}
                        onClick={() => { setActionError(null); setRejectModal(true); }}
                        disabled={actionLoading}
                      >
                        Reject
                      </Button>
                      <Button
                        variant="primary"
                        icon={CheckCircle2}
                        onClick={() => { setActionError(null); setApproveModal(true); }}
                        disabled={actionLoading}
                      >
                        Approve & Execute
                      </Button>
                    </div>
                  )}
                </>
              );
            })()
          ) : (
            <div className={styles.emptyDetail}>
              <ArrowRight size={28} color="var(--color-border)" />
              <p>Select a recommendation from the list to view details.</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Approval confirmation modal ─────────────────────────────────── */}
      <Modal
        isOpen={approveModal}
        onClose={() => setApproveModal(false)}
        title="Confirm Authorization"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setApproveModal(false)} disabled={actionLoading}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleApprove} disabled={actionLoading}>
              {actionLoading ? 'Saving…' : 'Confirm Execution'}
            </Button>
          </>
        }
      >
        <p className={styles.modalText}>
          You are authorizing:{' '}
          <strong>{selectedRec?.recommendation_text}</strong>
          {' '}for junction{' '}
          <strong>{selectedRec ? resolveJunction(selectedRec).name : ''}</strong>.
        </p>
        <p className={styles.modalSub}>
          This action is saved to the database and tied to your Operator ID.
          The physical signal implementation requires hardware integration (Phase 5 scope).
        </p>
      </Modal>

      {/* ── Rejection modal ─────────────────────────────────────────────── */}
      <Modal
        isOpen={rejectModal}
        onClose={() => setRejectModal(false)}
        title="Reject Recommendation"
        variant="danger"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setRejectModal(false)} disabled={actionLoading}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleReject} disabled={actionLoading}>
              {actionLoading ? 'Saving…' : 'Submit Rejection'}
            </Button>
          </>
        }
      >
        <div className={styles.rejectForm}>
          <label className={styles.rejectLabel}>Reason for Rejection</label>
          {REJECT_REASONS.map((r) => (
            <label key={r} className={styles.radioLabel}>
              <input
                type="radio"
                name="reason"
                value={r}
                checked={rejectReason === r}
                onChange={() => setRejectReason(r)}
              />
              {r}
            </label>
          ))}
          <label className={styles.rejectLabel} style={{ marginTop: 8 }}>
            Additional Context (optional)
          </label>
          <textarea
            className={styles.rejectNote}
            value={rejectNote}
            onChange={(e) => setRejectNote(e.target.value)}
            placeholder="Provide additional context if needed…"
            rows={3}
          />
        </div>
      </Modal>
    </div>
  );
}

// ── DataItem helper component ────────────────────────────────────────────────

function DataItem({ label, value, mono }) {
  return (
    <div className={styles.dataItem}>
      <span className={styles.dataLabel}>{label}</span>
      <span className={mono ? `${styles.dataValue} ${styles.mono}` : styles.dataValue}>
        {value}
      </span>
    </div>
  );
}
