// =====================================================
// SignalAI – Central Mock Data Store (Phase 1 Prototype)
// All data is SIMULATED for UI demonstration only.
// =====================================================

export const currentOperator = {
  id: 'OP-4092',
  name: 'J. Sharma',
  role: 'Traffic Operator',
  district: 'North District',
  email: 'j.sharma@signalai.gov.in',
  lastLogin: '2026-08-18 08:30',
};

// ── Junctions ──────────────────────────────────────
export const junctions = [
  { id: 'J-101', name: 'Genda Circle',      status: 'red',    density: 96, vehicles: 184, greenTime: 45, phase: 'N/S Green',  lat: 22.3056, lng: 73.1764, weather: 'Light Rain, 27°C' },
  { id: 'J-102', name: 'Kala Ghoda Circle',  status: 'red',    density: 88, vehicles: 162, greenTime: 40, phase: 'E/W Green',  lat: 22.3054, lng: 73.1818, weather: 'Clear, 29°C' },
  { id: 'J-103', name: 'Chakli Circle',      status: 'yellow', density: 62, vehicles: 98,  greenTime: 35, phase: 'N/S Green',  lat: 22.3086, lng: 73.1650, weather: 'Cloudy, 28°C' },
  { id: 'J-104', name: 'Fatehgunj Circle',   status: 'yellow', density: 55, vehicles: 87,  greenTime: 30, phase: 'E/W Green',  lat: 22.3207, lng: 73.1882, weather: 'Clear, 30°C' },
  { id: 'J-105', name: 'Amit Nagar Circle',  status: 'green',  density: 28, vehicles: 42,  greenTime: 30, phase: 'N/S Green',  lat: 22.3168, lng: 73.1975, weather: 'Clear, 30°C' },
  { id: 'J-106', name: 'Susen Circle',       status: 'green',  density: 18, vehicles: 26,  greenTime: 25, phase: 'All-way',    lat: 22.2994, lng: 73.2081, weather: 'Clear, 30°C' },
  { id: 'J-107', name: 'Muktanand Circle',   status: 'green',  density: 12, vehicles: 19,  greenTime: 25, phase: 'N/S Green',  lat: 22.3218, lng: 73.1979, weather: 'Clear, 29°C' },
  { id: 'J-108', name: 'Akota Circle',       status: 'red',    density: 92, vehicles: 175, greenTime: 50, phase: 'E/W Green',  lat: 22.2933, lng: 73.1721, weather: 'Humid, 31°C' },
];

// ── Dashboard KPIs ────────────────────────────────
export const kpiData = {
  totalJunctions:    315,
  activeSignals:     312,
  congestedJunctions: 8,
  pendingRecommendations: 12,
  activeEmergencyRoutes: 1,
  systemHealth:      99.1,
};

// ── Recommendations (Decision Queue) ──────────────
export const recommendations = [
  {
    id: 'AI-9042',
    junction: 'J-101',
    junctionName: 'Genda Circle',
    severity: 'red',
    currentDensity: 96,
    vehicleCount: 184,
    currentGreenTime: 45,
    suggestedGreenTime: 65,
    reason: 'Traffic density at Junction J-101 is significantly higher than nearby intersections along the Northbound corridor. A queue of approximately 400m has built up.',
    suggestedAction: 'Increase N/S green phase duration by +20 seconds.',
    expectedImpact: 'Estimated 45% reduction in average wait time, clearing the queue within 3–4 signal cycles.',
    createdAt: '10:42 AM',
    status: 'pending',
  },
  {
    id: 'AI-9041',
    junction: 'J-102',
    junctionName: 'Kala Ghoda Circle',
    severity: 'red',
    currentDensity: 88,
    vehicleCount: 162,
    currentGreenTime: 40,
    suggestedGreenTime: 52,
    reason: 'Eastbound vehicles are experiencing prolonged wait times due to insufficient green time relative to current peak load.',
    suggestedAction: 'Increase E/W green phase duration by +12 seconds.',
    expectedImpact: 'Estimated 30% improvement in flow. Cross-street wait time increase: ~6 seconds.',
    createdAt: '10:35 AM',
    status: 'pending',
  },
  {
    id: 'AI-9040',
    junction: 'J-103',
    junctionName: 'Chakli Circle',
    severity: 'yellow',
    currentDensity: 62,
    vehicleCount: 98,
    currentGreenTime: 35,
    suggestedGreenTime: 35,
    reason: 'Synchronize offset timing with adjacent Junction J-104 to create a coordinated green wave on the southbound corridor.',
    suggestedAction: 'Adjust signal offset by +8 seconds to match J-104 cycle.',
    expectedImpact: 'Improve corridor throughput by ~12%. No individual wait time increase.',
    createdAt: '10:20 AM',
    status: 'pending',
  },
  {
    id: 'AI-9039',
    junction: 'J-108',
    junctionName: 'Akota Circle',
    severity: 'red',
    currentDensity: 92,
    vehicleCount: 175,
    currentGreenTime: 50,
    suggestedGreenTime: 65,
    reason: 'Heavy congestion near the railway station due to train arrival. Historic patterns confirm peak load lasts ~15 minutes.',
    suggestedAction: 'Temporarily increase green time by +15 seconds for 10 cycles.',
    expectedImpact: 'Clear the post-arrival queue within estimated 12 minutes.',
    createdAt: '09:58 AM',
    status: 'pending',
  },
  {
    id: 'AI-9035',
    junction: 'J-104',
    junctionName: 'Fatehgunj Circle',
    severity: 'yellow',
    currentDensity: 55,
    vehicleCount: 87,
    currentGreenTime: 30,
    suggestedGreenTime: 36,
    reason: 'Moderate evening peak building ahead of schedule. Preventive adjustment recommended.',
    suggestedAction: 'Increase N/S green phase by +6 seconds.',
    expectedImpact: 'Pre-empt expected congestion. Maintain low severity rating.',
    createdAt: '09:30 AM',
    status: 'approved',
  },
  {
    id: 'AI-9030',
    junction: 'J-106',
    junctionName: 'Susen Circle',
    severity: 'green',
    currentDensity: 18,
    vehicleCount: 26,
    currentGreenTime: 25,
    suggestedGreenTime: 20,
    reason: 'Low traffic detected. Reducing cycle time will improve overall network rhythm.',
    suggestedAction: 'Reduce cycle time by 5 seconds.',
    expectedImpact: 'Marginal network efficiency improvement.',
    createdAt: '08:55 AM',
    status: 'rejected',
  },
];

// ── Analytics Data ────────────────────────────────
export const congestionTrend = [
  { time: '00:00', current: 12, baseline: 15 },
  { time: '02:00', current: 8,  baseline: 10 },
  { time: '04:00', current: 6,  baseline: 8  },
  { time: '06:00', current: 22, baseline: 20 },
  { time: '08:00', current: 78, baseline: 72 },
  { time: '10:00', current: 65, baseline: 60 },
  { time: '12:00', current: 55, baseline: 52 },
  { time: '14:00', current: 50, baseline: 48 },
  { time: '16:00', current: 80, baseline: 74 },
  { time: '18:00', current: 88, baseline: 80 },
  { time: '20:00', current: 48, baseline: 50 },
  { time: '22:00', current: 28, baseline: 30 },
];

export const peakHoursData = [
  { hour: '06:00', volume: 3200 },
  { hour: '07:00', volume: 8500 },
  { hour: '08:00', volume: 14100 },
  { hour: '09:00', volume: 9200 },
  { hour: '10:00', volume: 6800 },
  { hour: '11:00', volume: 5900 },
  { hour: '12:00', volume: 7200 },
  { hour: '13:00', volume: 6500 },
  { hour: '14:00', volume: 5800 },
  { hour: '15:00', volume: 6200 },
  { hour: '16:00', volume: 9800 },
  { hour: '17:00', volume: 13500 },
  { hour: '18:00', volume: 11200 },
  { hour: '19:00', volume: 7800 },
  { hour: '20:00', volume: 4500 },
  { hour: '21:00', volume: 2800 },
];

export const vehicleMovement = [
  { time: '06:00', entering: 1200, exiting: 900  },
  { time: '08:00', entering: 5800, exiting: 3200 },
  { time: '10:00', entering: 3800, exiting: 4200 },
  { time: '12:00', entering: 3100, exiting: 3500 },
  { time: '14:00', entering: 2900, exiting: 3100 },
  { time: '16:00', entering: 4200, exiting: 2800 },
  { time: '18:00', entering: 5100, exiting: 6200 },
  { time: '20:00', entering: 2200, exiting: 4500 },
  { time: '22:00', entering: 900,  exiting: 2100 },
];

export const junctionComparison = [
  { id: 'J-101', name: 'Genda Circle',   density: 96, avgWait: '1m 48s', aiActions: 6, severity: 'red'    },
  { id: 'J-108', name: 'Akota Circle',  density: 92, avgWait: '1m 35s', aiActions: 5, severity: 'red'    },
  { id: 'J-102', name: 'Kala Ghoda Circle',       density: 88, avgWait: '1m 12s', aiActions: 4, severity: 'red'    },
  { id: 'J-103', name: 'Chakli Circle',   density: 62, avgWait: '0m 48s', aiActions: 2, severity: 'yellow' },
  { id: 'J-104', name: 'Fatehgunj Circle',     density: 55, avgWait: '0m 32s', aiActions: 1, severity: 'yellow' },
];

// ── Emergency Routes ──────────────────────────────
export const emergencyHistory = [
  { id: 'ER-041', time: '09:14 AM', type: 'Ambulance', vehicleId: 'AMB-07', route: 'J-101 → J-103 → J-106', operator: 'OP-4092', status: 'Completed' },
  { id: 'ER-040', time: 'Yesterday', type: 'Fire Service', vehicleId: 'FIRE-E12', route: 'J-104 → J-108', operator: 'OP-3011', status: 'Completed' },
  { id: 'ER-039', time: 'Yesterday', type: 'Police', vehicleId: 'POL-P01', route: 'J-102 → J-101', operator: 'OP-4092', status: 'Completed' },
];

// ── Users (Admin) ──────────────────────────────────
export const users = [
  { id: 'OP-4092', name: 'J. Sharma',    email: 'j.sharma@signalai.gov.in',    role: 'Traffic Operator',     district: 'North',  status: 'active',   lastActive: '2 min ago' },
  { id: 'AD-1001', name: 'R. Mehta',     email: 'r.mehta@signalai.gov.in',     role: 'System Administrator', district: 'All',    status: 'active',   lastActive: '15 min ago' },
  { id: 'OP-4091', name: 'P. Verma',     email: 'p.verma@signalai.gov.in',     role: 'Traffic Operator',     district: 'South',  status: 'active',   lastActive: '1 hr ago' },
  { id: 'MA-2001', name: 'S. Gupta',     email: 's.gupta@municipal.gov.in',    role: 'Municipal Authority',  district: 'All',    status: 'active',   lastActive: '3 hr ago' },
  { id: 'ES-3001', name: 'A. Khan',      email: 'a.khan@emergency.gov.in',     role: 'Emergency Service',    district: 'North',  status: 'active',   lastActive: '5 hr ago' },
  { id: 'OP-4090', name: 'K. Singh',     email: 'k.singh@signalai.gov.in',     role: 'Traffic Operator',     district: 'East',   status: 'disabled', lastActive: '2 days ago' },
];

// ── Assistant Conversation Seed ───────────────────
export const assistantSeedMessages = [
  {
    id: 1,
    type: 'ai',
    text: 'Hello. I am the SignalAI Decision Support Assistant. I can help you understand traffic conditions, explain AI recommendations, and provide congestion strategies. How can I assist you?',
    timestamp: '10:40 AM',
  },
];

export const suggestedQuestions = [
  'Why is Junction J-101 congested?',
  'Show the busiest junctions right now',
  'Explain recommendation AI-9042',
  'What is the status of the North District?',
  'When was the last AI optimization applied?',
];

// ── Recent Activity ───────────────────────────────
export const recentActivity = [
  { time: '10:42 AM', event: 'Recommendation AI-9042 submitted for J-101', type: 'ai' },
  { time: '10:35 AM', event: 'Operator approved recommendation AI-9036', type: 'approved' },
  { time: '10:15 AM', event: 'Emergency Route ER-041 authorized (AMB-07)', type: 'emergency' },
  { time: '09:58 AM', event: 'Sensor offline alert: J-107 (resolved)', type: 'alert' },
  { time: '09:30 AM', event: 'Recommendation AI-9035 applied to J-104', type: 'approved' },
];
