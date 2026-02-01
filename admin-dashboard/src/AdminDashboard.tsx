import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AIMLHealth from './components/AIMLHealth';
import ClinicalMonitoring from './components/ClinicalMonitoring';
import SystemHealth from './components/SystemHealth';
import SecurityMonitoring from './components/SecurityMonitoring';
import DiseaseRanges from './components/DiseaseRanges';
import DiseaseProbability from './components/DiseaseProbability';
import MultimodalAnalysis from './components/MultimodalAnalysis';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});

type TabType = 'overview' | 'ai_ml' | 'clinical' | 'system' | 'security' | 'disease' | 'probability' | 'multimodal';

const TABS: { id: TabType; name: string; icon: string; short: string }[] = [
  { id: 'overview', name: 'نمای کلی', icon: '📊', short: 'Overview' },
  { id: 'ai_ml', name: 'سلامت AI/ML', icon: '🤖', short: 'AI/ML' },
  { id: 'clinical', name: 'کلینیکال', icon: '🏥', short: 'Clinical' },
  { id: 'multimodal', name: 'آنالیز مولتی‌مودال', icon: '🔬', short: 'Multimodal' },
  { id: 'disease', name: 'پارکینسون و آلزایمر', icon: '🧬', short: 'Disease Ranges' },
  { id: 'probability', name: 'احتمال بیماری', icon: '📈', short: 'Disease Probability' },
  { id: 'system', name: 'سیستم', icon: '⚙️', short: 'System' },
  { id: 'security', name: 'امنیت', icon: '🔐', short: 'Security' },
];

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-slate-50/80 flex">
        {/* Sidebar */}
        <aside
          className={`
          flex flex-col bg-white border-r border-slate-200/80 shadow-sm
          transition-all duration-300 ease-out
          ${sidebarOpen ? 'w-56' : 'w-20'}
        `}
        >
          <div className="flex items-center h-16 px-4 border-b border-slate-100 shrink-0">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-white font-bold shrink-0 shadow-md">
                N
              </div>
              {sidebarOpen && (
                <span className="font-semibold text-slate-800 truncate">
                  NeuroPredict
                </span>
              )}
            </div>
          </div>
          <nav className="flex-1 py-4 px-2 space-y-0.5 overflow-y-auto">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  w-full flex items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-all
                  ${activeTab === tab.id
                    ? 'bg-indigo-50 text-indigo-700 shadow-sm'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-800'
                  }
                `}
              >
                <span className="text-lg shrink-0 w-7 text-center">{tab.icon}</span>
                {sidebarOpen && (
                  <span className="font-medium truncate">{tab.name}</span>
                )}
              </button>
            ))}
          </nav>
          {sidebarOpen && (
            <div className="p-3 border-t border-slate-100 text-xs text-slate-400">
              Admin Dashboard v1
            </div>
          )}
        </aside>

        {/* Main */}
        <main className="flex-1 flex flex-col min-w-0">
          <header className="h-16 shrink-0 flex items-center justify-between px-6 lg:px-8 bg-white/80 backdrop-blur border-b border-slate-200/60">
            <div>
              <h1 className="text-xl font-bold text-slate-800">
                {TABS.find((t) => t.id === activeTab)?.short || 'Overview'}
              </h1>
              <p className="text-sm text-slate-500 mt-0.5">
                Real-time monitoring &amp; analytics
              </p>
            </div>
            <button
              type="button"
              onClick={() => setSidebarOpen((o) => !o)}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-700"
              aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
            >
              {sidebarOpen ? '◀' : '▶'}
            </button>
          </header>

          <div className="flex-1 p-6 lg:p-8 overflow-auto">
            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'ai_ml' && <AIMLHealth />}
            {activeTab === 'clinical' && <ClinicalMonitoring />}
            {activeTab === 'multimodal' && <MultimodalAnalysis />}
            {activeTab === 'disease' && <DiseaseRanges />}
            {activeTab === 'probability' && <DiseaseProbability />}
            {activeTab === 'system' && <SystemHealth />}
            {activeTab === 'security' && <SecurityMonitoring />}
          </div>
        </main>
      </div>
    </QueryClientProvider>
  );
}

function OverviewTab() {
  const cards = [
    {
      title: 'سلامت AI/ML',
      subtitle: 'Model drift, performance, feature importance',
      value: 'Monitoring',
      color: 'indigo',
      icon: '🤖',
    },
    {
      title: 'کلینیکال',
      subtitle: 'Longitudinal, smart alerts, prediction queue',
      value: 'Active',
      color: 'emerald',
      icon: '🏥',
    },
    {
      title: 'سلامت سیستم',
      subtitle: 'Latency, throughput, service status',
      value: 'Operational',
      color: 'violet',
      icon: '⚙️',
    },
    {
      title: 'امنیت و انطباق',
      subtitle: 'Audit logs, auth monitoring, admin activity',
      value: 'Secured',
      color: 'rose',
      icon: '🔐',
    },
  ];

  const colorMap: Record<string, string> = {
    indigo: 'from-indigo-50 to-white border-indigo-200 text-indigo-700',
    emerald: 'from-emerald-50 to-white border-emerald-200 text-emerald-700',
    violet: 'from-violet-50 to-white border-violet-200 text-violet-700',
    rose: 'from-rose-50 to-white border-rose-200 text-rose-700',
  };

  return (
    <div className="space-y-8">
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-800">
            به داشبورد مانیتورینگ خوش آمدید
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            NeuroPredict-AI Real-Time Monitoring — نمای یکپارچه از سلامت AI/ML،
            عملیات کلینیکی، عملکرد سیستم و انطباق امنیتی.
          </p>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {cards.map((card, i) => (
              <div
                key={i}
                className={`
                  rounded-xl border bg-gradient-to-br p-4 transition hover:shadow-md
                  ${colorMap[card.color]}
                `}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">
                      {card.title}
                    </p>
                    <p className="text-xl font-bold mt-1">{card.value}</p>
                    <p className="text-xs text-slate-500 mt-2">{card.subtitle}</p>
                  </div>
                  <span className="text-2xl opacity-80">{card.icon}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="text-base font-semibold text-slate-800">
              قابلیت‌های کلیدی
            </h3>
          </div>
          <ul className="p-6 space-y-3">
            {[
              'به‌روزرسانی برخط WebSocket',
              'تشخیص drift مدل AI/ML',
              'هشدارهای پشتیبانی تصمیم کلینیکی',
              'مانیتورینگ عملکرد سیستم',
              'ردیابی انطباق امنیتی',
              'ثبت ممیزی FDA/HIPAA',
            ].map((item, i) => (
              <li
                key={i}
                className="flex items-center gap-3 text-sm text-slate-700"
              >
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center text-xs font-bold">
                  ✓
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>
        <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="text-base font-semibold text-slate-800">
              قابلیت‌های مانیتورینگ
            </h3>
          </div>
          <ul className="p-6 space-y-3">
            {[
              'تحلیل Data drift و Performance drift',
              'توزیع امتیاز اطمینان',
              'توضیح‌پذیری اهمیت ویژگی',
              'هشدارهای هوشمند کلینیکی',
              'زمان پاسخ و توان عملیاتی',
              'مانیتورینگ رویدادهای امنیتی',
            ].map((item, i) => (
              <li
                key={i}
                className="flex items-center gap-3 text-sm text-slate-700"
              >
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-xs font-bold">
                  {i + 1}
                </span>
                {item}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
