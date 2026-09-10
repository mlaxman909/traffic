import styles from './Badge.module.css';

/**
 * Badge – Pill-shaped label for status, roles, severity
 * variant: 'green' | 'yellow' | 'red' | 'blue' | 'slate' | 'amber' | 'emerald'
 */
export default function Badge({ children, variant = 'slate', className = '' }) {
  return (
    <span className={[styles.badge, styles[variant], className].join(' ')}>
      {children}
    </span>
  );
}
