import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './Admin.css';

const Analytics = ({ users }) => {
  const COLORS = ['#2d6a4f', '#52b788', '#74c69d', '#95d5b2', '#b7e4c7', '#d8f3dc'];

  const analyticsData = useMemo(() => {
    // User growth over time (last 30 days)
    const today = new Date();
    const last30Days = Array.from({ length: 30 }, (_, i) => {
      const date = new Date(today);
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        users: 0,
      };
    });

    users.forEach(user => {
      const createdDate = new Date(user.created_at);
      const daysDiff = Math.floor((today - createdDate) / (1000 * 60 * 60 * 24));
      if (daysDiff >= 0 && daysDiff < 30) {
        const index = 29 - daysDiff;
        last30Days[index].users++;
      }
    });

    // Cumulative user growth
    let cumulative = 0;
    const cumulativeData = last30Days.map(day => {
      cumulative += day.users;
      return {
        ...day,
        total: cumulative,
      };
    });

    // User role distribution
    const roleData = [
      { name: 'Regular Users', value: users.filter(u => !u.is_admin).length },
      { name: 'Administrators', value: users.filter(u => u.is_admin).length },
    ];

    // User status distribution
    const statusData = [
      { name: 'Active', value: users.filter(u => u.is_active).length },
      { name: 'Inactive', value: users.filter(u => !u.is_active).length },
    ];

    // Recent signups (last 7 days by day of week)
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(today);
      date.setDate(date.getDate() - (6 - i));
      return {
        day: date.toLocaleDateString('en-US', { weekday: 'short' }),
        signups: 0,
      };
    });

    users.forEach(user => {
      const createdDate = new Date(user.created_at);
      const daysDiff = Math.floor((today - createdDate) / (1000 * 60 * 60 * 24));
      if (daysDiff >= 0 && daysDiff < 7) {
        const index = 6 - daysDiff;
        last7Days[index].signups++;
      }
    });

    return {
      growth: cumulativeData,
      dailySignups: last7Days,
      roles: roleData,
      status: statusData,
    };
  }, [users]);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div 
      className="analytics-section"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2>📊 Analytics Dashboard</h2>
      
      <div className="charts-grid">
        {/* User Growth Chart */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
        >
          <h3>User Growth (Last 30 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={analyticsData.growth}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="date" stroke="var(--text-secondary)" />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="total" 
                stroke="#2d6a4f" 
                strokeWidth={3}
                dot={{ fill: '#2d6a4f', r: 4 }}
                activeDot={{ r: 6 }}
                name="Total Users"
              />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Daily Signups Chart */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h3>Recent Signups (Last 7 Days)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={analyticsData.dailySignups}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="day" stroke="var(--text-secondary)" />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Bar dataKey="signups" fill="#52b788" name="New Signups" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* User Roles Distribution */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3>User Roles Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.roles}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {analyticsData.roles.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* User Status Distribution */}
        <motion.div 
          className="chart-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h3>User Status Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={analyticsData.status}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {analyticsData.status.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? '#52b788' : '#e63946'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Key Insights */}
      <motion.div 
        className="insights-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <h3>📈 Key Insights</h3>
        <div className="insights-grid">
          <div className="insight-card">
            <span className="insight-icon">📅</span>
            <div className="insight-content">
              <strong>Most Active Day</strong>
              <p>{analyticsData.dailySignups.reduce((max, day) => 
                day.signups > max.signups ? day : max, analyticsData.dailySignups[0]).day}
              </p>
            </div>
          </div>
          <div className="insight-card">
            <span className="insight-icon">📊</span>
            <div className="insight-content">
              <strong>Avg Daily Signups</strong>
              <p>
                {(analyticsData.dailySignups.reduce((sum, day) => sum + day.signups, 0) / 7).toFixed(1)} 
                {' '}users/day
              </p>
            </div>
          </div>
          <div className="insight-card">
            <span className="insight-icon">👥</span>
            <div className="insight-content">
              <strong>User Activity Rate</strong>
              <p>
                {users.length > 0 
                  ? ((analyticsData.status[0].value / users.length) * 100).toFixed(1) 
                  : 0}% active
              </p>
            </div>
          </div>
          <div className="insight-card">
            <span className="insight-icon">⚡</span>
            <div className="insight-content">
              <strong>Growth Trend</strong>
              <p>
                {analyticsData.dailySignups[6].signups >= analyticsData.dailySignups[0].signups 
                  ? '📈 Increasing' 
                  : '📉 Decreasing'}
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Analytics;
