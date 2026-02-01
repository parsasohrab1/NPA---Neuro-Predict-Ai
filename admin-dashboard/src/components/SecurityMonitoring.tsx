import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';

export default function SecurityMonitoring() {
  const { data: auditLogs, refetch: refetchLogs } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => monitoringApi.getAuditLogs(100, undefined, 24).then((res) => res.data),
    refetchInterval: 30000,
  });

  const { data: authMonitoring } = useQuery({
    queryKey: ['auth-monitoring'],
    queryFn: () => monitoringApi.getAuthenticationMonitoring(24).then((res) => res.data),
    refetchInterval: 30000,
  });

  const { data: adminActivity } = useQuery({
    queryKey: ['admin-activity'],
    queryFn: () => monitoringApi.getAdminActivity(24).then((res) => res.data),
    refetchInterval: 60000,
  });

  // WebSocket for real-time updates
  useWebSocket('security', (message) => {
    if (message.type === 'security_update') {
      refetchLogs();
    }
  });

  const highRiskLogs = auditLogs?.logs?.filter((log: any) => log.is_high_risk) || [];

  return (
    <div className="space-y-6">
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">🔐</span>
          <h2 className="text-lg font-semibold text-slate-800">Security & Compliance Monitoring</h2>
        </div>
        <div className="p-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="rounded-xl border border-rose-200 bg-gradient-to-br from-rose-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">High-Risk Activities</p>
              <p className="text-xl font-bold text-rose-600 mt-1">
                {auditLogs?.high_risk_count || 0}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-indigo-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Audit Logs</p>
              <p className="text-xl font-bold text-indigo-600 mt-1">
                {auditLogs?.total_count || 0}
              </p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Failed Logins</p>
              <p className="text-xl font-bold text-amber-600 mt-1">
                {authMonitoring?.login_statistics?.failed || 0}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-violet-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Active Admins</p>
              <p className="text-xl font-bold text-violet-600 mt-1">
                {adminActivity?.active_admin_count || 0}
              </p>
            </div>
          </div>

          {/* Authentication Monitoring */}
          {authMonitoring && (
            <div className="mb-6">
              <h3 className="text-base font-semibold text-slate-800 mb-3">Authentication Monitoring</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                  <h4 className="font-medium text-slate-700 mb-2">Login Statistics</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Attempts</span>
                    <span className="font-medium">
                      {authMonitoring.login_statistics?.total_attempts || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Successful</span>
                    <span className="font-medium text-green-600">
                      {authMonitoring.login_statistics?.successful || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Failed</span>
                    <span className="font-medium text-red-600">
                      {authMonitoring.login_statistics?.failed || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Success Rate</span>
                    <span className="font-medium">
                      {authMonitoring.login_statistics?.success_rate?.toFixed(1) || 0}%
                    </span>
                  </div>
                </div>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <h4 className="font-medium text-slate-700 mb-2">Security Alerts</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Brute Force IPs</span>
                    <span className="font-medium text-red-600">
                      {authMonitoring.security_alerts?.suspicious_activity_count || 0}
                    </span>
                  </div>
                  {authMonitoring.security_alerts?.brute_force_ips &&
                    authMonitoring.security_alerts.brute_force_ips.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-500 mb-1">Suspicious IPs:</p>
                        <div className="space-y-1">
                          {authMonitoring.security_alerts.brute_force_ips.map(
                            (ip: string, idx: number) => (
                              <div key={idx} className="text-xs bg-red-50 text-red-800 px-2 py-1 rounded">
                                {ip}
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            </div>

            {/* Recent Failed Logins */}
            {authMonitoring.recent_failed_logins &&
              authMonitoring.recent_failed_logins.length > 0 && (
                <div className="mt-4">
                  <h4 className="font-medium mb-2">Recent Failed Login Attempts</h4>
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {authMonitoring.recent_failed_logins.map((login: any, idx: number) => (
                      <div
                        key={idx}
                        className="bg-red-50 border-l-4 border-red-500 rounded p-3 text-sm"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium">{login.ip_address || 'Unknown IP'}</p>
                            <p className="text-gray-600 text-xs mt-1">{login.user_agent}</p>
                            {login.error && (
                              <p className="text-red-600 text-xs mt-1">{login.error}</p>
                            )}
                          </div>
                          <span className="text-xs text-gray-500">
                            {new Date(login.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
          </div>
        )}

        {/* High-Risk Audit Logs */}
        {highRiskLogs.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">High-Risk Activities</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {highRiskLogs.slice(0, 20).map((log: any, idx: number) => (
                <div
                  key={idx}
                  className="bg-red-50 border-l-4 border-red-500 rounded p-3 text-sm"
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-red-800">{log.action}</span>
                        <span className="text-xs text-gray-500">
                          {log.resource_type} #{log.resource_id}
                        </span>
                      </div>
                      <p className="text-gray-600 text-xs">
                        User ID: {log.user_id} | IP: {log.ip_address}
                      </p>
                    </div>
                    <div className="text-right">
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          log.success
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {log.success ? 'Success' : 'Failed'}
                      </span>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(log.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Admin Activity */}
        {adminActivity && (
          <div>
            <h3 className="text-base font-semibold text-slate-800 mb-3">Admin Activity</h3>
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 mb-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Active Admins:</span>
                  <span className="font-medium ml-2">
                    {adminActivity.active_admin_count} / {adminActivity.total_admin_count}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">Total Activities:</span>
                  <span className="font-medium ml-2">{adminActivity.total_activities}</span>
                </div>
              </div>
            </div>
            {adminActivity.activity_summary && adminActivity.activity_summary.length > 0 && (
              <div className="space-y-2">
                {adminActivity.activity_summary.map((activity: any, idx: number) => (
                  <div key={idx} className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 text-sm">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{activity.user_email}</p>
                        <p className="text-gray-600 text-xs mt-1">
                          {activity.activity_count} activities
                        </p>
                        {activity.recent_actions && activity.recent_actions.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {activity.recent_actions.map((action: string, actIdx: number) => (
                              <span
                                key={actIdx}
                                className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs"
                              >
                                {action}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {activity.last_activity
                          ? new Date(activity.last_activity).toLocaleString()
                          : 'N/A'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        </div>
      </section>
    </div>
  );
}

