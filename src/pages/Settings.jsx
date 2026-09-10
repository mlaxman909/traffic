import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Bell, Monitor, Shield, Users, LogOut } from 'lucide-react';
import Card, { CardHeader } from '../components/Shared/Card';
import Button from '../components/Shared/Button';
import FormInput, { FormSelect } from '../components/Shared/FormInput';
import Badge from '../components/Shared/Badge';
import { useAuth } from '../context/AuthContext';
import styles from './Settings.module.css';

const INNER_TABS = [
  { id: 'profile',   label: 'Operator Profile', icon: User },
  { id: 'notifs',    label: 'Notifications',    icon: Bell },
  { id: 'display',   label: 'Display',          icon: Monitor },
  { id: 'security',  label: 'Security',         icon: Shield },
];

const roleBadge = { 'Traffic Operator': 'green', 'System Administrator': 'dark', 'Municipal Authority': 'blue', 'Emergency Service': 'amber' };

export default function Settings() {
  const navigate = useNavigate();
  const { currentUser } = useAuth();
  const [tab, setTab]  = useState('profile');
  const [saved, setSaved] = useState(false);
  const [notifs, setNotifs] = useState({
    criticalCongestion: true,
    newRecommendation: true,
    emergencyRoute: true,
    sensorOffline: false,
    dailySummary: false,
  });

  function handleSave() {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  }

  return (
    <div className={styles.page}>
      {/* Inner Nav */}
      <div className={styles.innerNav}>
        <p className={styles.navSection}>Personal</p>
        {INNER_TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={[styles.navItem, tab === id ? styles.navActive : ''].join(' ')}
            onClick={() => setTab(id)}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
        <div className={styles.divider} />
        <p className={styles.navSection}>System</p>
        <button className={styles.navItem} onClick={() => navigate('/admin/users')}>
          <Users size={16} />
          User Management
        </button>
        <button className={[styles.navItem, styles.navDanger].join(' ')} onClick={() => navigate('/login')}>
          <LogOut size={16} />
          Sign Out
        </button>
      </div>

      {/* Content */}
      <div className={styles.content}>
        {saved && (
          <div className={styles.savedBanner}>✓ Settings saved successfully.</div>
        )}

        {tab === 'profile' && (
          <Card>
            <CardHeader title="Operator Profile" subtitle="Your identity and system assignment" />
            <div className={styles.profileTop}>
              <div className={styles.avatar}>{currentUser?.name?.charAt(0) || 'U'}</div>
              <div>
                <h3 className={styles.profileName}>{currentUser?.name || 'Loading...'}</h3>
                <Badge variant={roleBadge[currentUser?.role] || 'slate'}>{currentUser?.role}</Badge>
              </div>
            </div>
            <div className={styles.formGrid}>
              <FormInput id="name"     label="Full Name"     value={currentUser?.name || ''}     disabled />
              <FormInput id="opId"     label="Operator ID"   value={currentUser?.id || ''}       disabled />
              <FormInput id="email"    label="Email Address" value={currentUser?.email || ''}    disabled />
              <FormInput id="district" label="Assigned District" value={currentUser?.district || 'System Wide'} disabled />
              <FormInput id="role"     label="Role"          value={currentUser?.role || ''}     disabled />
              <FormInput id="last"     label="Last Login"    value={currentUser?.last_login ? new Date(currentUser.last_login).toLocaleString() : 'N/A'} disabled />
            </div>
            <div className={styles.actions}>
              <Button variant="secondary">Change Password</Button>
              <Button variant="primary" onClick={handleSave}>Save Changes</Button>
            </div>
          </Card>
        )}

        {tab === 'notifs' && (
          <Card>
            <CardHeader title="Notification Rules" subtitle="Configure what alerts you receive" />
            <div className={styles.checkList}>
              {[
                ['criticalCongestion', 'Alert on Critical Congestion (Red Status)'],
                ['newRecommendation',  'Alert on New AI Recommendation'],
                ['emergencyRoute',     'Alert when Emergency Route is Activated'],
                ['sensorOffline',      'Alert on Sensor Offline Events'],
                ['dailySummary',       'Receive Daily Traffic Summary Report'],
              ].map(([key, label]) => (
                <label key={key} className={styles.checkRow}>
                  <input
                    type="checkbox"
                    checked={notifs[key]}
                    onChange={(e) => setNotifs((n) => ({ ...n, [key]: e.target.checked }))}
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
            <div className={styles.actions}>
              <Button variant="primary" onClick={handleSave}>Save Preferences</Button>
            </div>
          </Card>
        )}

        {tab === 'display' && (
          <Card>
            <CardHeader title="Display Preferences" subtitle="Visual and layout settings" />
            <div className={styles.formGrid}>
              <FormSelect id="timezone" label="Timezone" options={['Asia/Kolkata (IST)', 'UTC', 'America/New_York']} />
              <FormSelect id="dateFormat" label="Date Format" options={['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD']} />
              <FormSelect id="density" label="Data Density" options={['Comfortable', 'Compact', 'Dense']} />
            </div>
            <div className={styles.actions}>
              <Button variant="primary" onClick={handleSave}>Save Display Settings</Button>
            </div>
          </Card>
        )}

        {tab === 'security' && (
          <Card>
            <CardHeader title="Security" subtitle="Manage your access credentials" />
            <div className={styles.formGrid}>
              <FormInput id="currentPw" label="Current Security Key" type="password" placeholder="••••••••" />
              <FormInput id="newPw"     label="New Security Key"     type="password" placeholder="Minimum 12 characters" />
              <FormInput id="confirmPw" label="Confirm New Key"      type="password" placeholder="Re-enter new key" />
            </div>
            <div className={styles.actions}>
              <Button variant="danger">Update Security Key</Button>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
