'use client';

import { useEffect, useState } from 'react';
import {
  Users,
  MessageCircle,
  ShoppingCart,
  IndianRupee,
  Smile,
  Activity,
  Wifi,
  Bot
} from 'lucide-react';

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || 'https://aria-api-1o1d.onrender.com';

interface DashboardData {
  metrics: {
    active_users: number;
    conversations_today: number;
    conversion_rate: number;
    average_order_value: number;
    revenue_today: number;
    satisfaction_score: number;
  };
  channel_breakdown: {
    whatsapp: number;
    web: number;
    mobile_app: number;
    store_kiosk: number;
  };
  agent_status: Record<string, string>;
  recent_activity: {
    type: string;
    user: string;
    message?: string;
    amount?: number;
    items?: number;
    result?: string;
    time: string;
  }[];
  timestamp: string;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`${API_URL}/api/v1/analytics/dashboard`);
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      const json = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const formatINR = (value: number) =>
    `₹${value.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`;

  const renderChannelBar = (label: string, value: number, color: string) => {
    const width = Math.min(100, value);
    return (
      <div className="space-y-1" key={label}>
        <div className="flex justify-between text-xs text-gray-600">
          <span>{label}</span>
          <span>{value}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-2 rounded-full ${color}`}
            style={{ width: `${width}%` }}
          ></div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-100 px-4 py-6 flex justify-center">
      <div className="w-full max-w-5xl bg-white rounded-2xl shadow-md border border-gray-200 p-5 space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              ARIA Control Center
            </h1>
            <p className="text-xs text-gray-500">
              Live view of your AI fashion assistant’s performance.
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <div className="flex items-center gap-1 px-2 py-1 rounded-full bg-green-50 text-green-700 border border-green-100">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              Live
            </div>
            {data && (
              <span className="text-gray-400">
                Updated at{' '}
                {new Date(data.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            )}
            <button
              onClick={fetchDashboard}
              className="px-3 py-1 rounded-full border border-gray-300 text-gray-700 hover:bg-gray-50 transition text-xs"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Loading / Error */}
        {loading && (
          <div className="py-10 text-center text-gray-500 text-sm">
            Loading analytics...
          </div>
        )}
        {error && !loading && (
          <div className="py-4 text-center text-red-500 text-sm">
            {error}
          </div>
        )}

        {/* Content */}
        {data && !loading && (
          <>
            {/* Top metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center">
                  <Users className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Active Users</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {data.metrics.active_users}
                  </p>
                </div>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center">
                  <MessageCircle className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Conversations Today</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {data.metrics.conversations_today}
                  </p>
                </div>
              </div>
              <div className="bg-gray-50 rounded-xl p-4 border border-gray-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <Activity className="w-4 h-4" />
                </div>
                <div>
                  <p className="text-xs text-gray-500">Conversion Rate</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {data.metrics.conversion_rate.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Revenue / AOV / CSAT */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="bg-white rounded-xl p-4 border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">
                    Average Order Value
                  </span>
                  <ShoppingCart className="w-4 h-4 text-gray-400" />
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {formatINR(data.metrics.average_order_value)}
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  Driven by ARIA-assisted journeys
                </p>
              </div>
              <div className="bg-white rounded-xl p-4 border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">Revenue Today</span>
                  <IndianRupee className="w-4 h-4 text-gray-400" />
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {formatINR(data.metrics.revenue_today)}
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  Estimated uplift from ARIA interactions
                </p>
              </div>
              <div className="bg-white rounded-xl p-4 border border-gray-100">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-500">
                    Satisfaction Score
                  </span>
                  <Smile className="w-4 h-4 text-gray-400" />
                </div>
                <p className="text-lg font-semibold text-gray-900">
                  {data.metrics.satisfaction_score.toFixed(1)}/5
                </p>
                <p className="text-[11px] text-gray-400 mt-1">
                  From post-conversation surveys
                </p>
              </div>
            </div>

            {/* Channel breakdown + Agent status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Channels */}
              <div className="bg-white rounded-xl p-4 border border-gray-100 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-gray-700">
                    Channel Mix (Last 24h)
                  </span>
                  <Wifi className="w-4 h-4 text-gray-400" />
                </div>
                <div className="space-y-3 mt-2 text-xs">
                  {renderChannelBar(
                    'WhatsApp',
                    data.channel_breakdown.whatsapp,
                    'bg-green-400'
                  )}
                  {renderChannelBar(
                    'Web Chat',
                    data.channel_breakdown.web,
                    'bg-blue-400'
                  )}
                  {renderChannelBar(
                    'Mobile App',
                    data.channel_breakdown.mobile_app,
                    'bg-purple-400'
                  )}
                  {renderChannelBar(
                    'In-Store Kiosk',
                    data.channel_breakdown.store_kiosk,
                    'bg-amber-400'
                  )}
                </div>
              </div>

              {/* Agent status */}
              <div className="bg-white rounded-xl p-4 border border-gray-100 space-y-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-gray-700">
                    Agent Mesh Status
                  </span>
                  <Bot className="w-4 h-4 text-gray-400" />
                </div>
                <div className="grid grid-cols-2 gap-2 mt-2 text-xs">
                  {Object.entries(data.agent_status).map(([name, status]) => (
                    <div
                      key={name}
                      className="flex items-center gap-2 px-2 py-1.5 bg-gray-50 rounded-lg border border-gray-100"
                    >
                      <span
                        className={`w-2 h-2 rounded-full ${
                          status === 'active'
                            ? 'bg-green-500'
                            : status === 'degraded'
                            ? 'bg-amber-500'
                            : 'bg-gray-400'
                        }`}
                      />
                      <span className="capitalize text-gray-700 text-[11px]">
                        {name.replace('_', ' ')}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recent activity */}
            <div className="bg-white rounded-xl p-4 border border-gray-100">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-gray-700">
                  Recent Activity
                </span>
              </div>
              <div className="divide-y divide-gray-100 text-xs">
                {data.recent_activity.map((item, idx) => (
                  <div key={idx} className="py-2 flex justify-between gap-4">
                    <div>
                      <p className="text-gray-800">
                        {item.type === 'conversation' && (
                          <>
                            <span className="font-medium">
                              {item.user}
                            </span>{' '}
                            had a conversation
                          </>
                        )}
                        {item.type === 'purchase' && (
                          <>
                            <span className="font-medium">
                              {item.user}
                            </span>{' '}
                            completed a purchase of{' '}
                            <span className="font-semibold">
                              {item.amount && formatINR(item.amount)}
                            </span>
                          </>
                        )}
                        {item.type === 'style_dna' && (
                          <>
                            <span className="font-medium">
                              {item.user}
                            </span>{' '}
                            completed Style DNA analysis
                          </>
                        )}
                      </p>
                      {item.message && (
                        <p className="text-gray-500 mt-0.5 line-clamp-1">
                          “{item.message}”
                        </p>
                      )}
                    </div>
                    <div className="text-gray-400 text-[11px]">
                      {item.time}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}