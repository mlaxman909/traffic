import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Login            from './pages/Login';
import Dashboard        from './pages/Dashboard';
import TrafficMap       from './pages/TrafficMap';
import Analytics        from './pages/Analytics';
import DecisionQueue    from './pages/DecisionQueue';
import EmergencyRouting from './pages/EmergencyRouting';
import Assistant        from './pages/Assistant';
import Settings         from './pages/Settings';
import AdminUsers       from './pages/AdminUsers';
import JunctionManagement from './pages/JunctionManagement';

import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Protected – wrapped in MainLayout */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard"         element={<Dashboard />} />
          <Route path="traffic-map"       element={<TrafficMap />} />
          <Route path="analytics"         element={<Analytics />} />
          <Route path="decision-queue"    element={<DecisionQueue />} />
          <Route path="emergency-routing" element={<EmergencyRouting />} />
          <Route path="assistant"         element={<Assistant />} />
          <Route path="settings"          element={<Settings />} />
          <Route path="admin/users"       element={
            <ProtectedRoute allowedRoles={['SYSTEM_ADMINISTRATOR']}>
              <AdminUsers />
            </ProtectedRoute>
          } />
          <Route path="admin/junctions"   element={
            <ProtectedRoute allowedRoles={['SYSTEM_ADMINISTRATOR']}>
              <JunctionManagement />
            </ProtectedRoute>
          } />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
