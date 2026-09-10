/**
 * src/pages/JunctionManagement.jsx
 * ==================================
 * Junction Management page — full CRUD connected to FastAPI/PostgreSQL.
 *
 * Operations:
 *   READ   → GET    /api/junctions
 *   CREATE → POST   /api/junctions
 *   UPDATE → PUT    /api/junctions/{id}
 *   DELETE → DELETE /api/junctions/{id}
 *
 * Schema fields (from backend JunctionCreate):
 *   junction_code (required), name (required), latitude, longitude,
 *   status, traffic_density, current_green_time, weather_condition
 *
 * NOTE: DELETE will cascade to traffic_records for that junction.
 *       The UI warns the user before allowing deletion of seed junctions.
 */

import { useState, useCallback, useEffect } from 'react';
import {
  MapPin, Plus, Edit2, Trash2, Inbox, CheckCircle, WifiOff, AlertTriangle,
} from 'lucide-react';
import Card, { CardHeader } from '../components/Shared/Card';
import Button from '../components/Shared/Button';
import Badge from '../components/Shared/Badge';
import Modal from '../components/Shared/Modal';
import FormInput, { FormSelect } from '../components/Shared/FormInput';
import { getJunctions, createJunction, updateJunction, deleteJunction } from '../services/api';
import styles from './AdminUsers.module.css'; // reuse the same table/form CSS

// ── Constants (must match backend JunctionStatus enum) ──────────────────────
const STATUS_OPTIONS = [
  { value: 'NORMAL',   label: 'Normal' },
  { value: 'MODERATE', label: 'Moderate' },
  { value: 'HIGH',     label: 'High' },
  { value: 'CRITICAL', label: 'Critical' },
  { value: 'OFFLINE',  label: 'Offline' },
];

const statusBadge = {
  NORMAL:   'green',
  MODERATE: 'yellow',
  HIGH:     'red',
  CRITICAL: 'red',
  OFFLINE:  'dark',
};

const EMPTY_FORM = {
  junction_code:      '',
  name:               '',
  latitude:           '',
  longitude:          '',
  status:             'NORMAL',
  traffic_density:    '',
  current_green_time: '',
  weather_condition:  '',
};

// ── Validation ───────────────────────────────────────────────────────────────
function validateForm(form, isEdit = false) {
  const errors = {};
  if (!isEdit && !form.junction_code.trim())
    errors.junction_code = 'Junction code is required (e.g. J-109).';
  if (!form.name.trim() || form.name.length < 2)
    errors.name = 'Junction name must be at least 2 characters.';
  if (form.latitude !== '' && (isNaN(Number(form.latitude)) || Number(form.latitude) < -90 || Number(form.latitude) > 90))
    errors.latitude = 'Latitude must be between -90 and 90.';
  if (form.longitude !== '' && (isNaN(Number(form.longitude)) || Number(form.longitude) < -180 || Number(form.longitude) > 180))
    errors.longitude = 'Longitude must be between -180 and 180.';
  if (form.traffic_density !== '' && (isNaN(Number(form.traffic_density)) || Number(form.traffic_density) < 0 || Number(form.traffic_density) > 100))
    errors.traffic_density = 'Traffic density must be 0–100.';
  if (form.current_green_time !== '' && (isNaN(Number(form.current_green_time)) || Number(form.current_green_time) < 0))
    errors.current_green_time = 'Green time must be a non-negative number.';
  return errors;
}

function buildPayload(form) {
  return {
    junction_code:      form.junction_code.trim(),
    name:               form.name.trim(),
    status:             form.status,
    latitude:           form.latitude !== '' ? parseFloat(form.latitude) : null,
    longitude:          form.longitude !== '' ? parseFloat(form.longitude) : null,
    traffic_density:    form.traffic_density !== '' ? parseInt(form.traffic_density, 10) : null,
    current_green_time: form.current_green_time !== '' ? parseInt(form.current_green_time, 10) : null,
    weather_condition:  form.weather_condition.trim() || null,
  };
}

// ── Inline UI helpers ────────────────────────────────────────────────────────
function Toast({ message, type }) {
  if (!message) return null;
  const color = type === 'success' ? 'var(--color-success)' : 'var(--color-danger)';
  const Icon  = type === 'success' ? CheckCircle : WifiOff;
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, padding:'10px 16px',
                  background:'var(--color-surface)', border:`1px solid ${color}`,
                  borderRadius:8, color, fontSize:'var(--text-sm)', marginBottom:12, fontWeight:500 }}>
      <Icon size={14} />
      <span>{message}</span>
    </div>
  );
}

function FieldError({ msg }) {
  return msg ? (
    <p style={{ color:'var(--color-danger)', fontSize:'var(--text-xs)', marginTop:4 }}>{msg}</p>
  ) : null;
}

// ── Main Component ───────────────────────────────────────────────────────────
export default function JunctionManagement() {
  const [junctions,    setJunctions]    = useState([]);
  const [loading,      setLoading]      = useState(true);
  const [toast,        setToast]        = useState({ message: '', type: '' });
  const [addModal,     setAddModal]     = useState(false);
  const [editTarget,   setEditTarget]   = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form,         setForm]         = useState(EMPTY_FORM);
  const [formErrors,   setFormErrors]   = useState({});
  const [saving,       setSaving]       = useState(false);
  const [deleting,     setDeleting]     = useState(false);

  // ── Load junctions ──────────────────────────────────────────────────────
  const loadJunctions = useCallback(async () => {
    setLoading(true);
    const { data, error } = await getJunctions();
    if (error) showToast(`Failed to load junctions: ${error}`, 'error');
    else       setJunctions(data || []);
    setLoading(false);
  }, []);

  useEffect(() => { loadJunctions(); }, [loadJunctions]);

  function showToast(message, type = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast({ message: '', type: '' }), 4500);
  }

  // ── Helpers ─────────────────────────────────────────────────────────────
  function handleChange(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (formErrors[field]) setFormErrors((e) => ({ ...e, [field]: '' }));
  }

  function openAdd() {
    setForm(EMPTY_FORM);
    setFormErrors({});
    setAddModal(true);
  }

  function openEdit(j) {
    setForm({
      junction_code:      j.junction_code,
      name:               j.name,
      latitude:           j.latitude ?? '',
      longitude:          j.longitude ?? '',
      status:             j.status,
      traffic_density:    j.traffic_density ?? '',
      current_green_time: j.current_green_time ?? '',
      weather_condition:  j.weather_condition ?? '',
    });
    setFormErrors({});
    setEditTarget(j);
  }

  // ── CREATE ───────────────────────────────────────────────────────────────
  async function handleCreate() {
    const errors = validateForm(form, false);
    if (Object.keys(errors).length) { setFormErrors(errors); return; }

    setSaving(true);
    const { data, error } = await createJunction(buildPayload(form));
    setSaving(false);

    if (error) {
      showToast(error, 'error');
    } else {
      setAddModal(false);
      await loadJunctions();
      showToast(`Junction "${data.junction_code} — ${data.name}" created successfully.`, 'success');
    }
  }

  // ── UPDATE ───────────────────────────────────────────────────────────────
  async function handleUpdate() {
    const errors = validateForm(form, true);
    if (Object.keys(errors).length) { setFormErrors(errors); return; }

    const payload = buildPayload(form);
    delete payload.junction_code; // junction_code is not updatable

    setSaving(true);
    const { data, error } = await updateJunction(editTarget.id, payload);
    setSaving(false);

    if (error) {
      showToast(error, 'error');
    } else {
      setEditTarget(null);
      await loadJunctions();
      showToast(`Junction "${data.junction_code}" updated successfully.`, 'success');
    }
  }

  // ── DELETE ───────────────────────────────────────────────────────────────
  async function handleDelete() {
    setDeleting(true);
    const { error } = await deleteJunction(deleteTarget.id);
    setDeleting(false);

    if (error) {
      showToast(error, 'error');
    } else {
      const code = deleteTarget.junction_code;
      setDeleteTarget(null);
      await loadJunctions();
      showToast(`Junction ${code} deleted from PostgreSQL.`, 'success');
    }
  }

  // ── Junction Form (shared for add/edit) ─────────────────────────────────
  function JunctionForm({ isEdit = false }) {
    return (
      <div className={styles.modalForm}>
        {!isEdit && (
          <div>
            <FormInput id="jCode" label="Junction Code" value={form.junction_code}
              onChange={(e) => handleChange('junction_code', e.target.value)}
              placeholder="e.g. J-109" />
            <FieldError msg={formErrors.junction_code} />
          </div>
        )}
        <div>
          <FormInput id="jName" label="Junction Name" value={form.name}
            onChange={(e) => handleChange('name', e.target.value)}
            placeholder="e.g. Park Rd & Market Ave" />
          <FieldError msg={formErrors.name} />
        </div>
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--space-4)' }}>
          <div>
            <FormInput id="jLat" label="Latitude" value={form.latitude}
              onChange={(e) => handleChange('latitude', e.target.value)}
              placeholder="e.g. 28.65" />
            <FieldError msg={formErrors.latitude} />
          </div>
          <div>
            <FormInput id="jLng" label="Longitude" value={form.longitude}
              onChange={(e) => handleChange('longitude', e.target.value)}
              placeholder="e.g. 77.21" />
            <FieldError msg={formErrors.longitude} />
          </div>
        </div>
        <FormSelect id="jStatus" label="Status" value={form.status}
          onChange={(e) => handleChange('status', e.target.value)}
          options={STATUS_OPTIONS} />
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'var(--space-4)' }}>
          <div>
            <FormInput id="jDensity" label="Traffic Density (%)" value={form.traffic_density}
              onChange={(e) => handleChange('traffic_density', e.target.value)}
              placeholder="0–100" />
            <FieldError msg={formErrors.traffic_density} />
          </div>
          <div>
            <FormInput id="jGreen" label="Green Time (s)" value={form.current_green_time}
              onChange={(e) => handleChange('current_green_time', e.target.value)}
              placeholder="e.g. 30" />
            <FieldError msg={formErrors.current_green_time} />
          </div>
        </div>
        <FormInput id="jWeather" label="Weather Condition (optional)" value={form.weather_condition}
          onChange={(e) => handleChange('weather_condition', e.target.value)}
          placeholder="e.g. Clear, 29°C" />
      </div>
    );
  }

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      <Toast message={toast.message} type={toast.type} />

      <Card padding={false}>
        <div className={styles.tableHeader}>
          <h1 className={styles.pageTitle}>Junction Management</h1>
          <div className={styles.controls}>
            <Button variant="primary" icon={Plus} onClick={openAdd}>
              Add Junction
            </Button>
          </div>
        </div>

        {loading ? (
          <div style={{ padding:32, textAlign:'center', color:'var(--color-text-secondary)',
                        fontSize:'var(--text-sm)' }}>
            Loading junctions from PostgreSQL…
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Code</th>
                <th>Name</th>
                <th>Status</th>
                <th>Density</th>
                <th>Green Time</th>
                <th>Coordinates</th>
                <th style={{ textAlign:'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {junctions.map((j) => (
                <tr key={j.id}>
                  <td className={styles.mono}>{j.junction_code}</td>
                  <td>{j.name}</td>
                  <td>
                    <Badge variant={statusBadge[j.status] || 'slate'}>{j.status}</Badge>
                  </td>
                  <td className={styles.mono}>
                    {j.traffic_density != null ? `${j.traffic_density}%` : '—'}
                  </td>
                  <td className={styles.mono}>
                    {j.current_green_time != null ? `${j.current_green_time}s` : '—'}
                  </td>
                  <td className={styles.mono} style={{ fontSize:'var(--text-xs)' }}>
                    {j.latitude != null && j.longitude != null
                      ? `${j.latitude}, ${j.longitude}`
                      : '—'}
                  </td>
                  <td>
                    <div className={styles.rowActions}>
                      <button className={styles.actionBtn} title="Edit junction"
                        onClick={() => openEdit(j)}>
                        <Edit2 size={14} />
                      </button>
                      <button
                        className={[styles.actionBtn, styles.actionDanger].join(' ')}
                        title="Delete junction"
                        onClick={() => setDeleteTarget(j)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className={styles.tableFooter}>
          <span>{junctions.length} junctions in PostgreSQL</span>
        </div>
      </Card>

      {/* ── Add Junction Modal ─────────────────────────────────────────── */}
      <Modal isOpen={addModal} onClose={() => setAddModal(false)}
        title="Register New Junction" size="md"
        footer={
          <>
            <Button variant="secondary" onClick={() => setAddModal(false)} disabled={saving}>Cancel</Button>
            <Button variant="primary" onClick={handleCreate} disabled={saving}>
              {saving ? 'Creating…' : 'Create Junction'}
            </Button>
          </>
        }
      >
        <JunctionForm isEdit={false} />
      </Modal>

      {/* ── Edit Junction Modal ────────────────────────────────────────── */}
      {editTarget && (
        <Modal isOpen={true} onClose={() => setEditTarget(null)}
          title={`Edit Junction: ${editTarget.junction_code}`} size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setEditTarget(null)} disabled={saving}>Cancel</Button>
              <Button variant="primary" onClick={handleUpdate} disabled={saving}>
                {saving ? 'Saving…' : 'Save Changes'}
              </Button>
            </>
          }
        >
          <JunctionForm isEdit={true} />
        </Modal>
      )}

      {/* ── Delete Confirmation Modal ──────────────────────────────────── */}
      {deleteTarget && (
        <Modal isOpen={true} onClose={() => setDeleteTarget(null)}
          title={`Delete Junction: ${deleteTarget.junction_code}`}
          variant="danger" size="sm"
          footer={
            <>
              <Button variant="secondary" onClick={() => setDeleteTarget(null)} disabled={deleting}>Cancel</Button>
              <Button variant="danger" onClick={handleDelete} disabled={deleting}>
                {deleting ? 'Deleting…' : 'Confirm Delete'}
              </Button>
            </>
          }
        >
          <div style={{ fontSize:'var(--text-sm)', lineHeight:1.7 }}>
            <div style={{ display:'flex', gap:8, alignItems:'flex-start', marginBottom:12,
                          padding:'10px 12px', background:'rgba(239,68,68,0.08)',
                          borderRadius:6, border:'1px solid rgba(239,68,68,0.3)' }}>
              <AlertTriangle size={16} color="var(--color-danger)" style={{ marginTop:2, flexShrink:0 }} />
              <p>
                <strong>Warning:</strong> Deleting junction <strong>{deleteTarget.junction_code}</strong> will
                also permanently delete all its associated traffic records (CASCADE) from PostgreSQL.
                This cannot be undone.
              </p>
            </div>
            <p>Junction: <strong>{deleteTarget.name}</strong></p>
          </div>
        </Modal>
      )}
    </div>
  );
}
