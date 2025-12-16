import React, { useState, useEffect } from 'react';

interface Appointment {
  id: number;
  name: string;
  email: string;
  phone: string;
  service_type: string;
  preferred_date: string;
  preferred_time: string;
  message: string | null;
  status: string;
  created_at: string;
}

interface Stats {
  total: number;
  pending: number;
  confirmed: number;
}

const Admin: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [stats, setStats] = useState<Stats>({ total: 0, pending: 0, confirmed: 0 });
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const API_URL = process.env.REACT_APP_API_URL || '';
  const ADMIN_TOKEN = 'wallet-wealth-admin-2024';

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (password === ADMIN_TOKEN) {
      setIsAuthenticated(true);
      setError('');
      fetchData();
    } else {
      setError('Invalid admin password');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch appointments
      const appointmentsRes = await fetch(
        `${API_URL}/api/appointments?admin_token=${ADMIN_TOKEN}`
      );
      const appointmentsData = await appointmentsRes.json();
      setAppointments(appointmentsData.appointments || []);

      // Fetch stats
      const statsRes = await fetch(
        `${API_URL}/api/appointments/stats?admin_token=${ADMIN_TOKEN}`
      );
      const statsData = await statsRes.json();
      setStats(statsData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchData();
      // Auto-refresh every 30 seconds
      const interval = setInterval(fetchData, 30000);
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-[calc(100vh-80px)] bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full mx-4">
          <div className="bg-white rounded-2xl shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-ww-navy rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔐</span>
              </div>
              <h1 className="text-2xl font-bold text-ww-navy">Admin Access</h1>
              <p className="text-gray-500 mt-2">Enter admin password to continue</p>
            </div>

            <form onSubmit={handleLogin}>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Admin password"
                className="input-field mb-4"
                autoFocus
              />
              {error && (
                <p className="text-red-500 text-sm mb-4">{error}</p>
              )}
              <button type="submit" className="w-full btn-primary">
                Login
              </button>
            </form>

            <p className="text-xs text-gray-400 mt-4 text-center">
              Hint: wallet-wealth-admin-2024
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-80px)] bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-ww-navy">Appointment Dashboard</h1>
            <p className="text-gray-500">Manage consultation requests</p>
          </div>
          <button
            onClick={fetchData}
            disabled={loading}
            className="btn-outline flex items-center"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <span className="mr-2">🔄</span>
            )}
            Refresh
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-ww-navy">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Appointments</p>
                <p className="text-3xl font-bold text-ww-navy">{stats.total}</p>
              </div>
              <span className="text-4xl">📅</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-yellow-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Pending</p>
                <p className="text-3xl font-bold text-yellow-600">{stats.pending}</p>
              </div>
              <span className="text-4xl">⏳</span>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Confirmed</p>
                <p className="text-3xl font-bold text-green-600">{stats.confirmed}</p>
              </div>
              <span className="text-4xl">✅</span>
            </div>
          </div>
        </div>

        {/* Appointments Table */}
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="px-6 py-4 bg-ww-navy text-white">
            <h2 className="text-xl font-semibold">Recent Appointments</h2>
          </div>

          {appointments.length === 0 ? (
            <div className="p-12 text-center">
              <span className="text-6xl">📭</span>
              <p className="text-gray-500 mt-4">No appointments yet</p>
              <p className="text-gray-400 text-sm">Appointments will appear here when clients book</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Client</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Contact</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Service</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Date & Time</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase">Booked On</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {appointments.map((appointment) => (
                    <tr key={appointment.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">{appointment.name}</div>
                        {appointment.message && (
                          <div className="text-sm text-gray-500 truncate max-w-xs" title={appointment.message}>
                            "{appointment.message}"
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <a href={`tel:${appointment.phone}`} className="text-ww-navy hover:underline">
                            📞 {appointment.phone}
                          </a>
                        </div>
                        <div className="text-sm">
                          <a href={`mailto:${appointment.email}`} className="text-gray-500 hover:underline">
                            ✉️ {appointment.email}
                          </a>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                          {appointment.service_type}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium">{appointment.preferred_date}</div>
                        <div className="text-sm text-gray-500">{appointment.preferred_time}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          appointment.status === 'pending' 
                            ? 'bg-yellow-100 text-yellow-800'
                            : appointment.status === 'confirmed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {appointment.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(appointment.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Admin;
