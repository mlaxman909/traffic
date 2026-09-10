import { useState, useRef, useEffect } from 'react';
import { Send, Activity, RotateCcw } from 'lucide-react';
import { assistantSeedMessages, suggestedQuestions, junctions } from '../data/mockData';
import Badge from '../components/Shared/Badge';
import styles from './Assistant.module.css';

// Simulate canned AI responses based on keywords
function generateResponse(input) {
  const q = input.toLowerCase();

  if (q.includes('j-101') || q.includes('main st') || q.includes('congested') || q.includes('why')) {
    return {
      text: 'Traffic density at Junction J-101 (Genda Circle) is currently at 96% — significantly higher than the network average of 52%.\n\nAnalysis: A queue of approximately 400m has formed on the Northbound approach due to insufficient green-phase duration relative to the current vehicle arrival rate.\n\nSuggested Strategy: Increasing the N/S green phase by +20 seconds may improve flow and clear the queue within 3–4 signal cycles.\n\nA formal recommendation (AI-9042) is available in the Decision Queue for your review and approval.',
      context: 'J-101',
    };
  }
  if (q.includes('busiest') || q.includes('worst') || q.includes('top')) {
    return {
      text: 'Currently, the top 3 most congested junctions are:\n\n1. J-101 (Genda Circle) — 96% density\n2. J-108 (Akota Circle) — 92% density\n3. J-102 (Kala Ghoda Circle) — 88% density\n\nAll three have pending recommendations in the Decision Queue.',
      context: 'J-101',
    };
  }
  if (q.includes('ai-9042') || q.includes('recommend')) {
    return {
      text: 'Recommendation AI-9042 was generated at 10:42 AM for Junction J-101.\n\nSuggested Action: Increase N/S green phase by +20 seconds (from 45s to 65s).\n\nExpected Impact: 45% reduction in average wait time, clearing a 400m queue within 3–4 cycles.\n\nStatus: Pending your approval in the Decision Queue. I cannot apply this automatically.',
      context: 'J-101',
    };
  }
  if (q.includes('north') || q.includes('district')) {
    return {
      text: 'North District Status Summary:\n\n• Total monitored junctions: 48\n• Congested: 5 (High)\n• Moderate: 12\n• Low / Normal: 31\n\nThe primary concern is the Main St corridor (J-101 to J-103). Average wait times in this corridor are currently 1m 45s, 22% above the 7-day baseline.',
      context: null,
    };
  }
  return {
    text: "I don't have specific information for that query in the current prototype dataset. Please try asking about a specific junction (e.g., J-101), the busiest roads, or a specific recommendation ID.",
    context: null,
  };
}

export default function Assistant() {
  const [messages, setMessages] = useState(assistantSeedMessages);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [activeContext, setActiveContext] = useState(null);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function sendMessage(text) {
    const q = text || input.trim();
    if (!q) return;

    const userMsg = { id: Date.now(), type: 'user', text: q, timestamp: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) };
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setLoading(true);

    setTimeout(() => {
      const { text: reply, context } = generateResponse(q);
      const aiMsg = { id: Date.now() + 1, type: 'ai', text: reply, timestamp: new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) };
      setMessages((m) => [...m, aiMsg]);
      if (context) setActiveContext(context);
      setLoading(false);
    }, 1000);
  }

  const contextJunction = junctions.find((j) => j.id === activeContext);

  return (
    <div className={styles.page}>
      {/* Chat Pane */}
      <div className={styles.chatPane}>
        <div className={styles.chatHeader}>
          <div className={styles.chatTitle}>
            <Activity size={18} color="var(--color-primary)" />
            <div>
              <h2>SignalAI Assistant (Phase 7 Prototype)</h2>
              <p>Static mockup — Not connected to live LLM or DB</p>
            </div>
          </div>
          <button className={styles.clearBtn} onClick={() => { setMessages(assistantSeedMessages); setActiveContext(null); }}
            title="Clear conversation">
            <RotateCcw size={15} /> Clear
          </button>
        </div>

        <div className={styles.chatHistory}>
          {messages.map((msg) => (
            <div key={msg.id} className={[styles.message, msg.type === 'user' ? styles.userMsg : styles.aiMsg].join(' ')}>
              {msg.type === 'ai' && (
                <div className={styles.aiAvatar}><Activity size={14} /></div>
              )}
              <div className={styles.bubble}>
                <p className={styles.bubbleText}>{msg.text}</p>
                <span className={styles.timestamp}>{msg.timestamp}</span>
              </div>
            </div>
          ))}

          {loading && (
            <div className={[styles.message, styles.aiMsg].join(' ')}>
              <div className={styles.aiAvatar}><Activity size={14} /></div>
              <div className={styles.bubble}>
                <div className={styles.typing}>
                  <span /><span /><span />
                </div>
                <p className={styles.thinkingText}>Analyzing traffic data...</p>
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className={styles.inputArea}>
          <div className={styles.pills}>
            {suggestedQuestions.slice(0, 3).map((q) => (
              <button key={q} className={styles.pill} onClick={() => sendMessage(q)}>{q}</button>
            ))}
          </div>
          <form className={styles.inputForm} onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
            <input
              className={styles.chatInput}
              placeholder="Ask SignalAI about traffic conditions..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              aria-label="Message input"
            />
            <button type="submit" className={styles.sendBtn} disabled={loading || !input.trim()} aria-label="Send">
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>

      {/* Context Pane */}
      <div className={styles.contextPane}>
        <div className={styles.contextTitle}>
          {activeContext ? `Live Context: ${activeContext}` : 'Context Panel'}
        </div>

        {contextJunction ? (
          <>
            {/* Mini Map */}
            <div className={styles.miniMapBox}>
              <svg viewBox="0 0 100 60" className={styles.miniMapSvg}>
                <line x1="50" y1="0" x2="50" y2="60" stroke="#e2e8f0" strokeWidth="8" />
                <line x1="0" y1="30" x2="100" y2="30" stroke="#e2e8f0" strokeWidth="8" />
                <line x1="50" y1="0" x2="50" y2="60" stroke={contextJunction.status === 'red' ? '#ef4444' : contextJunction.status === 'yellow' ? '#eab308' : '#22c55e'} strokeWidth="2" />
                <line x1="0" y1="30" x2="100" y2="30" stroke={contextJunction.status === 'red' ? '#ef4444' : '#22c55e'} strokeWidth="2" />
                <circle cx="50" cy="30" r="5" fill={contextJunction.status === 'red' ? '#ef4444' : contextJunction.status === 'yellow' ? '#eab308' : '#22c55e'} stroke="#fff" strokeWidth="1.5" />
                <text x="50" y="22" textAnchor="middle" fontSize="5" fill="#0f172a" fontFamily="Inter">{contextJunction.id}</text>
              </svg>
              <p className={styles.miniMapLabel}>{contextJunction.name}</p>
            </div>

            <div className={styles.contextData}>
              <ContextRow label="Status"        value={<Badge variant={contextJunction.status}>{contextJunction.status.toUpperCase()}</Badge>} />
              <ContextRow label="Vehicle Count" value={`${contextJunction.vehicles} / min`} />
              <ContextRow label="Density"       value={`${contextJunction.density}%`} />
              <ContextRow label="Active Phase"  value={contextJunction.phase} />
              <ContextRow label="Green Time"    value={`${contextJunction.greenTime}s`} />
              <ContextRow label="Weather"       value={contextJunction.weather} />
            </div>

            <div className={styles.contextNote}>
              <Activity size={13} />
              Verify this data against the Traffic Map before acting on AI suggestions.
            </div>
          </>
        ) : (
          <div className={styles.contextEmpty}>
            <Activity size={28} color="var(--color-border)" />
            <p>Context data appears here when you ask about a specific junction.</p>
          </div>
        )}
      </div>
    </div>
  );
}

function ContextRow({ label, value }) {
  return (
    <div className={styles.ctxRow}>
      <span className={styles.ctxLabel}>{label}</span>
      <span className={styles.ctxValue}>{value}</span>
    </div>
  );
}
