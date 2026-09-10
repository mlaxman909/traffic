/**
 * src/pages/AdminUsers.jsx
 * ==========================
 * User Management page — full CRUD connected to FastAPI/PostgreSQL.
 *
 * Operations:
 *   READ   → GET  /api/users
 *   CREATE → POST /api/users
 *   UPDATE → PUT  /api/users/{id}
 *   DELETE → DELETE /api/users/{id}
 *
 * All operations show loading states, success messages, and error messages.
 * Existing Phase 1 UI components and layout are preserved.
 */

import { useState, useEffect, useCallback } from 'react';
import { Search, UserPlus, Edit2, Trash2, Inbox, WifiOff, CheckCircle } from 'lucide-react';
import Card, { CardHeader } from '../components/Shared/Card';
import Button from '../components/Shared/Button';
import Badge from '../components/Shared/Badge';
import Modal from '../components/Shared/Modal';
import FormInput, { FormSelect } from '../components/Shared/FormInput';
import { getUsers, createUser, updateUser, deleteUser } from '../services/api';
import styles from './AdminUsers.module.css';

// ── Constants matching backend enums ────────────────────────────────────────
const ROLE_OPTIONS = [
  { value: 'TRAFFIC_OPERATOR',     label: 'Traffic Operator' },
  { value: 'SYSTEM_ADMINISTRATOR', label: 'System Administrator' },
  { value: 'MUNICIPAL_AUTHORITY',  label: 'Municipal Authority' },
  { value: 'EMERGENCY_SERVICE',    label: 'Emergency Service' },
];
const ROLES_DISPLAY = Object.fromEntries(ROLE_OPTIONS.map((r) => [r.value, r.label]));
const DISTRICT_OPTIONS = ['North', 'South', 'East', 'West', 'All'];
const STATUS_OPTIONS = [
  { value: 'ACTIVE',   label: 'Active' },
  { value: 'INACTIVE', label: 'Inactive' },
];
const ROLE_FILTER_OPTIONS = [{ value: 'All', label: 'All Roles' }, ...ROLE_OPTIONS];

const roleBadge = {
  TRAFFIC_OPERATOR:     'green',
  SYSTEM_ADMINISTRATOR: 'dark',
  MUNICIPAL_AUTHORITY:  'blue',
  EMERGENCY_SERVICE:    'amber',
};

const EMPTY_FORM = {
  name: '', email: '', role: 'TRAFFIC_OPERATOR',
  status: 'ACTIVE', district: 'North',
};

// ── Inline feedback components ───────────────────────────────────────────────
function Toast({ message, type }) {
  if (!message) return null;
  const color = type === 'success' ? 'var(--color-success)' : 'var(--color-danger)';
  const Icon  = type === 'success' ? CheckCircle : WifiOff;
  return (
    <div style={{ display:'flex', alignItems:'center', gap:8, padding:'10px 16px',
                  background:'var(--color-surface)', border:`1px solid ${color}`,
                  borderRadius:8, color, fontSize:'var(--text-sm)', marginBottom:12,
                  fontWeight:500 }}>
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

// ── Validation ───────────────────────────────────────────────────────────────
function validateUserForm(form) {
  const errors = {};
  if (!form.name.trim())          errors.name  = 'Full name is required.';
  else if (form.name.length < 2)  errors.name  = 'Name must be at least 2 characters.';
  if (!form.email.trim())         errors.email = 'Email is required.';
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
                                  errors.email = 'Enter a valid email address.';
  if (!form.role)                 errors.role  = 'Role is required.';
  return errors;
}

// ── Main Component ───────────────────────────────────────────────────────────
export default function AdminUsers() {
  const [users,       setUsers]       = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [toast,       setToast]       = useState({ message: '', type: '' });
  const [search,      setSearch]      = useState('');
  const [roleFilter,  setRoleFilter]  = useState('All');

  // Modal states
  const [addModal,     setAddModal]     = useState(false);
  const [editUser,     setEditUser]     = useState(null);   // user object being edited
  const [deleteTarget, setDeleteTarget] = useState(null);   // user to delete

  // Form state
  const [form,       setForm]       = useState(EMPTY_FORM);
  const [formErrors, setFormErrors] = useState({});
  const [saving,     setSaving]     = useState(false);
  const [deleting,   setDeleting]   = useState(false);

  // ── Fetch users from API ────────────────────────────────────────────────
  const loadUsers = useCallback(async () => {
    setLoading(true);
    const { data, error } = await getUsers();
    if (error) {
      showToast(`Could not load users: ${error}`, 'error');
    } else {
      setUsers(data || []);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadUsers(); }, [loadUsers]);

  function showToast(message, type = 'success') {
    setToast({ message, type });
    setTimeout(() => setToast({ message: '', type: '' }), 4000);
  }

  // ── Filtered list ───────────────────────────────────────────────────────
  const filtered = users.filter((u) => {
    const matchSearch = u.name.toLowerCase().includes(search.toLowerCase()) ||
                        u.email.toLowerCase().includes(search.toLowerCase());
    const matchRole   = roleFilter === 'All' || u.role === roleFilter;
    return matchSearch && matchRole;
  });

  // ── Form helpers ─────────────────────────────────────────────────────────
  function handleFormChange(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
    if (formErrors[field]) setFormErrors((e) => ({ ...e, [field]: '' }));
  }

  function openAddModal() {
    setForm(EMPTY_FORM);
    setFormErrors({});
    setAddModal(true);
  }

  function openEditModal(user) {
    setForm({
      name:     user.name,
      email:    user.email,
      role:     user.role,
      status:   user.status,
      district: user.district || 'North',
    });
    setFormErrors({});
    setEditUser(user);
  }

  // ── CREATE ───────────────────────────────────────────────────────────────
  async function handleCreate() {
    const errors = validateUserForm(form);
    if (Object.keys(errors).length > 0) { setFormErrors(errors); return; }

    setSaving(true);
    const { data, error } = await createUser(form);
    setSaving(false);

    if (error) {
      showToast(error, 'error');
    } else {
      setAddModal(false);
      await loadUsers();
      showToast(`User "${data.name}" created successfully.`, 'success');
    }
  }

  // ── UPDATE ───────────────────────────────────────────────────────────────
  async function handleUpdate() {
    const errors = validateUserForm(form);
    if (Object.keys(errors).length > 0) { setFormErrors(errors); return; }

    setSaving(true);
    const { data, error } = await updateUser(editUser.id, {
      name:     form.name,
      email:    form.email,
      role:     form.role,
      status:   form.status,
      district: form.district || null,
    });
    setSaving(false);

    if (error) {
      showToast(error, 'error');
    } else {
      setEditUser(null);
      await loadUsers();
      showToast(`User "${data.name}" updated successfully.`, 'success');
    }
  }

  // ── DELETE ───────────────────────────────────────────────────────────────
  async function handleDelete() {
    setDeleting(true);
    const { error } = await deleteUser(deleteTarget.id);
    setDeleting(false);

    if (error) {
      showToast(error, 'error');
    } else {
      const name = deleteTarget.name;
      setDeleteTarget(null);
      await loadUsers();
      showToast(`User "${name}" deleted successfully.`, 'success');
    }
  }

  // ── Render ───────────────────────────────────────────────────────────────
  return (
    <div className={styles.page}>
      <Toast message={toast.message} type={toast.type} />

      <Card padding={false}>
        <div className={styles.tableHeader}>
          <h1 className={styles.pageTitle}>User Management</h1>
          <div className={styles.controls}>
            <div className={styles.searchWrap}>
              <Search size={14} className={styles.searchIcon} />
              <input
                className={styles.searchInput}
                placeholder="Search users..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <FormSelect
              id="roleFilter"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              options={ROLE_FILTER_OPTIONS}
            />
            <Button variant="primary" icon={UserPlus} onClick={openAddModal}>
              Add New User
            </Button>
          </div>
        </div>

        {loading ? (
          <div style={{ padding:32, textAlign:'center', color:'var(--color-text-secondary)',
                        fontSize:'var(--text-sm)' }}>
            Loading users from PostgreSQL…
          </div>
        ) : filtered.length === 0 ? (
          <div className={styles.empty}>
            <Inbox size={32} color="var(--color-border)" />
            <p>No users found matching your search criteria.</p>
            <Button variant="secondary" size="sm" onClick={() => { setSearch(''); setRoleFilter('All'); }}>
              Clear Filters
            </Button>
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Operator Name</th>
                <th>ID</th>
                <th>Role</th>
                <th>District</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.id}>
                  <td>
                    <div className={styles.userCell}>
                      <div className={styles.userAvatar}>{u.name.charAt(0)}</div>
                      <div>
                        <p className={styles.userName}>{u.name}</p>
                        <p className={styles.userEmail}>{u.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className={styles.mono}>#{u.id}</td>
                  <td><Badge variant={roleBadge[u.role] || 'slate'}>{ROLES_DISPLAY[u.role] || u.role}</Badge></td>
                  <td>{u.district || '—'}</td>
                  <td>
                    <span className={[styles.statusDot, u.status === 'ACTIVE' ? styles.statusActive : styles.statusDisabled].join(' ')} />
                    {u.status === 'ACTIVE' ? 'Active' : 'Inactive'}
                  </td>
                  <td>
                    <div className={styles.rowActions}>
                      <button className={styles.actionBtn} title="Edit user"
                        onClick={() => openEditModal(u)}>
                        <Edit2 size={14} />
                      </button>
                      <button
                        className={[styles.actionBtn, styles.actionDanger].join(' ')}
                        title="Delete user"
                        onClick={() => setDeleteTarget(u)}
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
          <span>
            Showing {filtered.length} of {users.length} users — from PostgreSQL
          </span>
        </div>
      </Card>

      {/* ── Add User Modal ─────────────────────────────────────────────── */}
      <Modal
        isOpen={addModal}
        onClose={() => setAddModal(false)}
        title="Provision New Operator"
        size="md"
        footer={
          <>
            <Button variant="secondary" onClick={() => setAddModal(false)} disabled={saving}>Cancel</Button>
            <Button variant="primary" onClick={handleCreate} disabled={saving}>
              {saving ? 'Creating…' : 'Create User'}
            </Button>
          </>
        }
      >
        <div className={styles.modalForm}>
          <div>
            <FormInput id="newName" label="Full Name" value={form.name}
              onChange={(e) => handleFormChange('name', e.target.value)}
              placeholder="e.g. Jane Doe" />
            <FieldError msg={formErrors.name} />
          </div>
          <div>
            <FormInput id="newEmail" label="Email Address" value={form.email}
              onChange={(e) => handleFormChange('email', e.target.value)}
              placeholder="e.g. jane.doe@signalai.gov.in" />
            <FieldError msg={formErrors.email} />
          </div>
          <div>
            <FormSelect id="newRole" label="System Role" value={form.role}
              onChange={(e) => handleFormChange('role', e.target.value)}
              options={ROLE_OPTIONS} />
            <FieldError msg={formErrors.role} />
          </div>
          <FormSelect id="newDistrict" label="District Assignment" value={form.district}
            onChange={(e) => handleFormChange('district', e.target.value)}
            options={DISTRICT_OPTIONS} />
          <FormSelect id="newStatus" label="Account Status" value={form.status}
            onChange={(e) => handleFormChange('status', e.target.value)}
            options={STATUS_OPTIONS} />
          {form.role === 'SYSTEM_ADMINISTRATOR' && (
            <div className={styles.roleWarning}>
              ⚠ System Administrator role grants full access to user management and system configuration.
            </div>
          )}
        </div>
      </Modal>

      {/* ── Edit User Modal ────────────────────────────────────────────── */}
      {editUser && (
        <Modal isOpen={true} onClose={() => setEditUser(null)}
          title={`Edit User: ${editUser.name}`} size="md"
          footer={
            <>
              <Button variant="secondary" onClick={() => setEditUser(null)} disabled={saving}>Cancel</Button>
              <Button variant="primary" onClick={handleUpdate} disabled={saving}>
                {saving ? 'Saving…' : 'Save Changes'}
              </Button>
            </>
          }
        >
          <div className={styles.modalForm}>
            <div>
              <FormInput id="editName" label="Full Name" value={form.name}
                onChange={(e) => handleFormChange('name', e.target.value)} />
              <FieldError msg={formErrors.name} />
            </div>
            <div>
              <FormInput id="editEmail" label="Email Address" value={form.email}
                onChange={(e) => handleFormChange('email', e.target.value)} />
              <FieldError msg={formErrors.email} />
            </div>
            <FormSelect id="editRole" label="Role Assignment" value={form.role}
              onChange={(e) => handleFormChange('role', e.target.value)}
              options={ROLE_OPTIONS} />
            <FormSelect id="editDistrict" label="District" value={form.district || 'North'}
              onChange={(e) => handleFormChange('district', e.target.value)}
              options={DISTRICT_OPTIONS} />
            <FormSelect id="editStatus" label="Account Status" value={form.status}
              onChange={(e) => handleFormChange('status', e.target.value)}
              options={STATUS_OPTIONS} />
          </div>
        </Modal>
      )}

      {/* ── Delete Confirmation Modal ──────────────────────────────────── */}
      {deleteTarget && (
        <Modal isOpen={true} onClose={() => setDeleteTarget(null)}
          title={`Delete Account: ${deleteTarget.name}`}
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
          <p style={{ fontSize: 'var(--text-sm)', lineHeight: 1.6 }}>
            This will permanently delete <strong>{deleteTarget.name}</strong> (#{deleteTarget.id}) from PostgreSQL.
            This action cannot be undone.
          </p>
        </Modal>
      )}
    </div>
  );
}
