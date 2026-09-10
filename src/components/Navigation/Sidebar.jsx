import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Map, BarChart2, InboxIcon,
  AlertTriangle, Bot, Settings, ChevronLeft, ChevronRight,
  Activity, Users2, TrafficCone,
} from 'lucide-react';
import styles from './Sidebar.module.css';

const navItems = [
  { to: '/dashboard',            label: 'Dashboard',           icon: LayoutDashboard },
  { to: '/traffic-map',          label: 'Traffic Map',          icon: Map             },
  { to: '/analytics',            label: 'Analytics',            icon: BarChart2       },
  { to: '/decision-queue',       label: 'Decision Queue',       icon: InboxIcon       },
  { to: '/emergency-routing',    label: 'Emergency Routing',    icon: AlertTriangle   },
  { to: '/assistant',            label: 'SignalAI Assistant',   icon: Bot             },
  { to: '/admin/junctions',      label: 'Junction Mgmt',        icon: TrafficCone     },
  { to: '/admin/users',          label: 'User Management',      icon: Users2          },
  { to: '/settings',             label: 'Settings',             icon: Settings        },
];

export default function Sidebar({ collapsed, onToggle }) {
  return (
    <aside className={[styles.sidebar, collapsed ? styles.collapsed : ''].join(' ')}>
      {/* Brand */}
      <div className={styles.brand}>
        <div className={styles.logo}>
          <Activity size={22} color="#22c55e" />
        </div>
        {!collapsed && (
          <div className={styles.brandText}>
            <span className={styles.brandName}>SignalAI</span>
            <span className={styles.brandSub}>Traffic Control</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className={styles.nav} aria-label="Main navigation">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [styles.navItem, isActive ? styles.active : ''].join(' ')
            }
            title={collapsed ? label : undefined}
          >
            <Icon size={18} className={styles.navIcon} />
            {!collapsed && <span className={styles.navLabel}>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle */}
      <button className={styles.collapseBtn} onClick={onToggle} aria-label="Toggle sidebar">
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {/* System Status (footer) */}
      {!collapsed && (
        <div className={styles.statusBar}>
          <span className={styles.statusDot} />
          <span className={styles.statusText}>System Online</span>
        </div>
      )}
    </aside>
  );
}
