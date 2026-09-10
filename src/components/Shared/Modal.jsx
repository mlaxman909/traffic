import { useEffect } from 'react';
import { X } from 'lucide-react';
import Button from './Button';
import styles from './Modal.module.css';

/**
 * Modal – Standard dialog overlay
 * variant: 'default' | 'danger'
 */
export default function Modal({ isOpen, onClose, title, children, footer, variant = 'default', size = 'md' }) {
  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true" onClick={(e) => e.target === e.currentTarget && onClose()}>
      <div className={[styles.dialog, styles[size], variant === 'danger' ? styles.danger : ''].join(' ')}>
        <div className={styles.header}>
          <h3 className={styles.title}>{title}</h3>
          <button className={styles.closeBtn} onClick={onClose} aria-label="Close dialog">
            <X size={18} />
          </button>
        </div>
        <div className={styles.body}>{children}</div>
        {footer && <div className={styles.footer}>{footer}</div>}
      </div>
    </div>
  );
}
