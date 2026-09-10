import styles from './FormInput.module.css';

/**
 * FormInput – Text / Email / Password input
 */
export default function FormInput({
  id,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  required = false,
  disabled = false,
  rightElement,
  ...rest
}) {
  return (
    <div className={styles.group}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
          {required && <span className={styles.required} aria-hidden="true"> *</span>}
        </label>
      )}
      <div className={styles.inputWrap}>
        <input
          id={id}
          type={type}
          className={[styles.input, error ? styles.hasError : ''].join(' ')}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          aria-describedby={error ? `${id}-error` : undefined}
          {...rest}
        />
        {rightElement && <div className={styles.rightEl}>{rightElement}</div>}
      </div>
      {error && (
        <p id={`${id}-error`} className={styles.errorText} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

/**
 * FormSelect – Dropdown select
 */
export function FormSelect({ id, label, value, onChange, options = [], required, disabled, error }) {
  return (
    <div className={styles.group}>
      {label && (
        <label htmlFor={id} className={styles.label}>
          {label}
          {required && <span className={styles.required}> *</span>}
        </label>
      )}
      <select
        id={id}
        className={[styles.input, styles.select, error ? styles.hasError : ''].join(' ')}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
      >
        {options.map((opt) =>
          typeof opt === 'string' ? (
            <option key={opt} value={opt}>{opt}</option>
          ) : (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          )
        )}
      </select>
      {error && <p className={styles.errorText}>{error}</p>}
    </div>
  );
}
