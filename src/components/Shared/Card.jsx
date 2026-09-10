import styles from './Card.module.css';

/**
 * Card – Standard surface container
 */
export default function Card({ children, className = '', padding = true }) {
  return (
    <div className={[styles.card, padding ? styles.padded : '', className].join(' ')}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }) {
  return (
    <div className={styles.header}>
      <div>
        <h3 className={styles.title}>{title}</h3>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
