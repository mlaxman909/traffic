import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Navigation/Sidebar';
import Header from '../components/Navigation/Header';
import styles from './MainLayout.module.css';

export default function MainLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={[styles.layout, collapsed ? styles.sidebarCollapsed : ''].join(' ')}>
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((p) => !p)} />
      <div className={styles.content}>
        <Header />
        <main className={styles.main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
