import Badge from './Badge';
import styles from './KpiCard.module.css';

const severityMap = { green: 'green', yellow: 'yellow', red: 'red' };

/**
 * KpiCard – High-level metric display for dashboard
 */
export default function KpiCard({ title, value, subtitle, icon: Icon, indicator, trend, trendLabel }) {
  const trendPositive = trend && !String(trend).startsWith('-');

  return (
    <div className={styles.card}>
      <div className={styles.top}>
        <p className={styles.title}>{title}</p>
        {Icon && (
          <div className={styles.iconWrap}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className={styles.valueRow}>
        <span className={styles.value}>{value}</span>
        {indicator && (
          <Badge variant={severityMap[indicator] || 'slate'}>
            <span className={[styles.dot, styles[indicator]].join(' ')} />
          </Badge>
        )}
      </div>
      {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
      {trend && (
        <p className={[styles.trend, trendPositive ? styles.trendUp : styles.trendDown].join(' ')}>
          {trendPositive ? '▲' : '▼'} {trend} {trendLabel}
        </p>
      )}
    </div>
  );
}
