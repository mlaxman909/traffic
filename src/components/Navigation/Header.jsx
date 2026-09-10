import { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Bell, Clock, LogOut, Settings, ChevronDown } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import styles from './Header.module.css';

const routeLabels = {
  '/dashboard':         'Overview Dashboard',
  '/traffic-map':       'Traffic Map',
  '/analytics':         'Analytics',
  '/decision-queue':    'Decision Queue',
  '/emergency-routing': 'Emergency Routing',
  '/assistant':         'SignalAI Assistant',
  '/settings':          'Settings',
  '/admin/users':       'User Management',
};

function useTime() {
  const [time, setTime] = useState(new Date());
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);
  return time;
}

export default function Header() {
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const time = useTime();
  const { currentUser, logout } = useAuth();
  const label = routeLabels[pathname] || 'SignalAI';

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleLogout() {
    setDropdownOpen(false);
    logout();
    navigate('/login');
  }

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <div className={styles.breadcrumb}>
          <span className={styles.breadHome}>SignalAI</span>
          <span className={styles.sep}>/</span>
          <span className={styles.breadCurrent}>{label}</span>
        </div>
      </div>

      <div className={styles.right}>
        <div className={styles.clock}>
          <Clock size={14} />
          <span>{time.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
        </div>

        <button className={styles.iconBtn} title="Notifications" aria-label="Notifications">
          <Bell size={18} />
          <span className={styles.notifBadge}>3</span>
        </button>

        {/* Profile Dropdown */}
        <div className={styles.profileWrap} ref={dropdownRef}>
          <button
            className={styles.profile}
            onClick={() => setDropdownOpen((o) => !o)}
            aria-haspopup="true"
            aria-expanded={dropdownOpen}
          >
            <div className={styles.avatar}>
              {currentUser?.name?.charAt(0) || 'O'}
            </div>
            <div className={styles.profileInfo}>
              <span className={styles.profileName}>{currentUser?.name || 'Operator'}</span>
              <span className={styles.profileRole}>{currentUser?.role || 'TRAFFIC_OPERATOR'}</span>
            </div>
            <ChevronDown
              size={14}
              className={[styles.chevron, dropdownOpen ? styles.chevronOpen : ''].join(' ')}
            />
          </button>

          {dropdownOpen && (
            <div className={styles.dropdown} role="menu">
              <div className={styles.dropdownHeader}>
                <p className={styles.dropdownName}>{currentUser?.name}</p>
                <p className={styles.dropdownId}>{currentUser?.email}</p>
              </div>
              <div className={styles.dropdownDivider} />
              <button
                className={styles.dropdownItem}
                onClick={() => { setDropdownOpen(false); navigate('/settings'); }}
                role="menuitem"
              >
                <Settings size={14} />
                Settings
              </button>
              <div className={styles.dropdownDivider} />
              <button
                className={[styles.dropdownItem, styles.dropdownLogout].join(' ')}
                onClick={handleLogout}
                role="menuitem"
              >
                <LogOut size={14} />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
