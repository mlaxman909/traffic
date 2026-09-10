import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLocation } from 'react-router-dom';
import { Eye, EyeOff, Activity, AlertCircle, Loader } from 'lucide-react';
import FormInput from '../components/Shared/FormInput';
import Button from '../components/Shared/Button';
import { useAuth } from '../context/AuthContext';
import styles from './Login.module.css';

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  
  const [form, setForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Where to send them after successful login
  const from = location.state?.from?.pathname || '/dashboard';

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (error) setError('');
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!form.email.trim() || !form.password.trim()) {
      setError('Email and Security Key are required.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await login(form.email, form.password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Authentication failed. Verify Email and Security Key.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.page}>
      {/* Background grid pattern */}
      <div className={styles.bg} aria-hidden="true" />

      <div className={styles.card}>
        {/* Brand */}
        <div className={styles.brand}>
          <div className={styles.logoWrap}>
            <Activity size={28} color="#22c55e" />
          </div>
          <h1 className={styles.brandName}>SignalAI</h1>
          <p className={styles.brandSub}>Municipal Traffic Control Portal</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className={styles.errorBanner} role="alert">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        {/* Form */}
        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          <FormInput
            id="email"
            name="email"
            label="Email Address"
            placeholder="Enter your email"
            value={form.email}
            onChange={handleChange}
            required
            autoComplete="username"
          />

          <FormInput
            id="password"
            name="password"
            label="Security Key"
            type={showPassword ? 'text' : 'password'}
            placeholder="••••••••"
            value={form.password}
            onChange={handleChange}
            required
            autoComplete="current-password"
            rightElement={
              <button
                type="button"
                className={styles.eyeBtn}
                onClick={() => setShowPassword((p) => !p)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            }
          />

          <div className={styles.forgotRow}>
            <button type="button" className={styles.forgotLink}>
              Reset Security Key
            </button>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            loading={loading}
            icon={loading ? undefined : undefined}
          >
            {loading ? 'Verifying...' : 'Authenticate & Enter'}
          </Button>
        </form>

        {/* Hint */}
        <p className={styles.hint}>
          <strong>Demo:</strong> <code>j.sharma@signalai.gov.in</code> / <code>password123</code>
        </p>
      </div>

      <footer className={styles.footer}>
        SignalAI Traffic Management System v1.0 &nbsp;•&nbsp; Authorized Personnel Only &nbsp;•&nbsp; Phase 4 Security
      </footer>
    </div>
  );
}
