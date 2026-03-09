import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowRight, Check, Search, BarChart2, Zap, AlertTriangle,
  ChevronRight, Download, Bell, Share2, PlayCircle, Image as ImageIcon,
  TrendingUp, Users, Target, Shield
} from 'lucide-react';
import clsx from 'clsx';
import { mockData } from './data';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// --- STAGE COMPONENTS ---

const Stage1_Onboarding = ({ onComplete }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [selectedCompetitors, setSelectedCompetitors] = useState(
    mockData.onboarding.competitors.filter(c => c.selected).map(c => c.id)
  );

  const handleStartAnalysis = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onComplete();
    }, 2500); // 2.5s simulated loading
  };

  const toggleCompetitor = (id) => {
    if (selectedCompetitors.includes(id)) {
      setSelectedCompetitors(selectedCompetitors.filter(c => c !== id));
    } else {
      if (selectedCompetitors.length < 3) {
        setSelectedCompetitors([...selectedCompetitors, id]);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center">
        <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mb-6"></div>
        <h2 className="text-xl font-semibold mb-2">Analyzing Market Data...</h2>
        <p className="text-muted text-sm">Scanning 250+ competitor ads and campaigns</p>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto py-12">
      <div className="text-center mb-10">
        <div className="w-12 h-12 bg-primary-light text-primary rounded-xl flex items-center justify-center mx-auto mb-4">
          <Search size={24} />
        </div>
        <h1 className="text-3xl font-bold mb-2">Let's refine your competitive landscape</h1>
        <p className="text-muted">We've auto-detected these details based on your domain.</p>
      </div>

      <div className="card mb-8">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase text-muted mb-1">Company Name</label>
            <input type="text" value={mockData.user.company} readOnly className="w-full p-3 bg-gray-50 rounded-md border border-gray-200 text-gray-700" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-muted mb-1">Industry</label>
            <input type="text" value={mockData.user.industry} readOnly className="w-full p-3 bg-gray-50 rounded-md border border-gray-200 text-gray-700" />
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-muted mb-1">Website</label>
            <input type="text" value={mockData.user.website} readOnly className="w-full p-3 bg-gray-50 rounded-md border border-gray-200 text-gray-700" />
          </div>
        </div>
      </div>

      <div className="mb-8">
        <label className="block font-semibold mb-4">Select top 3 competitors to track:</label>
        <div className="space-y-3">
          {mockData.onboarding.competitors.map(comp => (
            <div
              key={comp.id}
              onClick={() => toggleCompetitor(comp.id)}
              className={clsx(
                "flex items-center p-4 rounded-lg border cursor-pointer transition-all",
                selectedCompetitors.includes(comp.id)
                  ? "border-primary bg-primary-light/10 ring-1 ring-primary"
                  : "border-gray-200 hover:border-gray-300 bg-white"
              )}
            >
              <div className={clsx(
                "w-5 h-5 rounded border flex items-center justify-center mr-4 transition-colors",
                selectedCompetitors.includes(comp.id) ? "bg-primary border-primary text-white" : "border-gray-300"
              )}>
                {selectedCompetitors.includes(comp.id) && <Check size={12} />}
              </div>
              <span className="flex-1 font-medium">{comp.name}</span>
            </div>
          ))}
        </div>
      </div>

      <button onClick={handleStartAnalysis} className="w-full btn btn-primary text-lg h-12">
        Start Analysis <ArrowRight size={18} />
      </button>
    </div>
  );
};

const Stage2_Dashboard = ({ onNavigate }) => {
  return (
    <div className="space-y-8 animate-fade-in">
      <header className="flex justify-between items-center mb-8">
        <div>
          <span className="text-sm font-semibold text-muted tracking-wider uppercase">Dashboard</span>
          <h1 className="text-3xl font-bold mt-1">Market Overview</h1>
        </div>
        <div className="text-right text-sm text-muted">
          Last updated: Just now
        </div>
      </header>

      {/* Key Insights */}
      <section>
        <h3 className="text-sm font-bold text-muted uppercase tracking-wider mb-4 flex items-center gap-2">
          <Zap size={16} className="text-warning" /> Key Insights
        </h3>
        <div className="card border-l-4 border-l-warning p-6 relative overflow-hidden">
          <div className="flex flex-col md:flex-row gap-6 items-start">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="badge badge-warning flex items-center gap-1">
                  <AlertTriangle size={12} /> Urgent Opportunity
                </span>
                <span className="text-sm text-muted">Jan 29, 2026</span>
              </div>
              <h2 className="text-2xl font-bold mb-3">{mockData.dashboard.alerts[0].title}</h2>
              <div className="space-y-2 text-gray-600 mb-6">
                <p className="flex items-start gap-2">
                  <ArrowRight size={16} className="mt-1 flex-shrink-0 text-gray-400" />
                  Mamaearth launched winter campaign on Jan 15
                </p>
                <p className="flex items-start gap-2">
                  <ArrowRight size={16} className="mt-1 flex-shrink-0 text-gray-400" />
                  <strong>40% increase in ad spend</strong> detected
                </p>
                <p className="flex items-start gap-2">
                  <ArrowRight size={16} className="mt-1 flex-shrink-0 text-gray-400" />
                  Targeting "dry skin winter care" keyword
                </p>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                <h4 className="flex items-center gap-2 font-semibold text-blue-900 mb-2">
                  <TrendingUp size={16} /> Recommended Action
                </h4>
                <p className="text-blue-800">
                  Launch counter-campaign by <strong>Jan 25</strong> targeting "winter skincare for sensitive skin" (gap opportunity)
                </p>
              </div>
            </div>

            <div className="flex flex-col gap-3 min-w-[200px]">
              <button
                onClick={() => onNavigate('deep_dive')}
                className="btn btn-primary w-full"
              >
                View Full Analysis
              </button>
              <button className="btn btn-outline w-full">Export Strategy Brief</button>
            </div>
          </div>
        </div>
      </section>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Market Position */}
        <section>
          <h3 className="text-sm font-bold text-muted uppercase tracking-wider mb-4">Market Share (Ad Volume)</h3>
          <div className="card h-full">
            <div className="h-[250px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockData.dashboard.marketPosition} layout="vertical" margin={{ left: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis type="category" dataKey="name" width={100} tick={{ fontSize: 12 }} />
                  <Tooltip cursor={{ fill: 'transparent' }} />
                  <Bar dataKey="ads" radius={[0, 4, 4, 0]} barSize={24}>
                    {mockData.dashboard.marketPosition.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.isLeader ? '#ef4444' : entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between text-sm">
              <div>
                <span className="block text-muted text-xs">Your Strategy</span>
                <span className="font-semibold">Solutions-focused</span>
              </div>
              <div className="text-right">
                <span className="block text-muted text-xs">Market Trend</span>
                <span className="font-semibold text-indigo-600">Problem-focused</span>
              </div>
            </div>
          </div>
        </section>

        {/* Porter's Five Forces */}
        <section>
          <h3 className="text-sm font-bold text-muted uppercase tracking-wider mb-4">Porter's Five Forces</h3>
          <div className="card h-full space-y-5">
            {mockData.dashboard.porter.map((item, i) => (
              <div key={i}>
                <div className="flex justify-between mb-1 text-sm">
                  <span className="font-medium">{item.label}</span>
                  <span className="text-muted">{item.score}/10 ({item.level})</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={clsx("h-full rounded-full", {
                      "bg-red-500": item.score >= 7,
                      "bg-yellow-500": item.score >= 5 && item.score < 7,
                      "bg-green-500": item.score < 5
                    })}
                    style={{ width: `${(item.score / 10) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
};

const Stage3_DeepDive = ({ onNavigate }) => {
  return (
    <div className="animate-fade-in space-y-8">
      <button onClick={() => onNavigate('dashboard')} className="text-sm text-muted hover:text-primary flex items-center gap-1 mb-4">
        <ChevronRight size={16} className="rotate-180" /> Back to Dashboard
      </button>

      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded bg-red-100 text-red-600 flex items-center justify-center font-bold text-xl">M</div>
          <h1 className="text-3xl font-bold">Mamaearth <span className="text-muted font-normal text-xl">Marketing Strategy Decoded</span></h1>
        </div>
      </header>

      {/* Creative Analysis Gallery */}
      <section>
        <div className="flex justify-between items-end mb-4">
          <h3 className="text-lg font-bold">Ad Creative Analysis</h3>
          <span className="text-sm text-muted">Last 30 Days</span>
        </div>
        <div className="card p-0 overflow-hidden mb-6">
          <div className="grid grid-cols-4 divide-x divide-gray-100 bg-gray-50 h-48">
            {mockData.deepDive.ads.map((ad, i) => (
              <div key={i} className="relative group flex items-center justify-center bg-gray-200/50 hover:bg-gray-200 transition-colors cursor-pointer">
                <div className="text-gray-400 font-medium flex flex-col items-center">
                  {ad.type === 'video' ? <PlayCircle size={32} /> : <ImageIcon size={32} />}
                  <span className="text-xs mt-2">{ad.date}</span>
                </div>
                <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
            ))}
          </div>
          <div className="p-6 grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-indigo-500"></div> Visual Theme</h4>
              <p className="text-sm font-medium mb-1">{mockData.deepDive.analysis.visualTheme}</p>
              <p className="text-xs text-muted">Evidence: {mockData.deepDive.analysis.visualEvidence}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-emerald-500"></div> Color Palette</h4>
              <p className="text-sm font-medium mb-1">{mockData.deepDive.analysis.colors}</p>
              <p className="text-xs text-muted">Evidence: {mockData.deepDive.analysis.colorsEvidence}</p>
            </div>
            <div>
              <h4 className="font-semibold mb-2 flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-amber-500"></div> Target Demo</h4>
              <p className="text-sm font-medium mb-1">{mockData.deepDive.analysis.target}</p>
              <p className="text-xs text-muted">Evidence: {mockData.deepDive.analysis.targetEvidence}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="grid md:grid-cols-2 gap-8">
        {/* Messaging Strategy */}
        <section className="card">
          <div className="border-b border-gray-100 p-4">
            <h3 className="font-bold flex items-center gap-2"><Target size={18} /> Messaging Strategy</h3>
          </div>
          <div className="p-4 space-y-6">
            <div>
              <span className="text-xs font-semibold uppercase text-muted tracking-wide mb-3 block">Top Keywords</span>
              <div className="flex flex-wrap gap-2">
                {mockData.deepDive.messaging.keywords.map((kw, i) => (
                  <span key={i} className="badge badge-neutral bg-gray-50">
                    {kw.text} <span className="opacity-50 ml-1">x{kw.count}</span>
                  </span>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-purple-50 p-3 rounded-lg">
                <span className="text-xs text-purple-600 font-bold uppercase">Primary Hook</span>
                <p className="font-semibold text-gray-800">{mockData.deepDive.messaging.primaryHook}</p>
              </div>
              <div className="bg-blue-50 p-3 rounded-lg">
                <span className="text-xs text-blue-600 font-bold uppercase">Secondary Hook</span>
                <p className="font-semibold text-gray-800">{mockData.deepDive.messaging.secondaryHook}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Competitive Gaps */}
        <section className="card border-l-4 border-l-emerald-500">
          <div className="border-b border-gray-100 p-4 flex justify-between items-center">
            <h3 className="font-bold flex items-center gap-2"><Zap size={18} className="text-emerald-500" /> Competitive Gaps</h3>
            <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded">YOUR OPPORTUNITY</span>
          </div>
          <div className="divide-y divide-gray-100">
            {mockData.deepDive.gaps.map((gap, i) => (
              <div key={i} className="p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start gap-3">
                  <span className="text-emerald-500 font-bold mt-1">0{i + 1}</span>
                  <div>
                    <h4 className="font-semibold text-gray-900">{gap.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">→ {gap.impact}</p>
                    <p className="text-xs text-muted mt-1">{gap.stat}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="p-4 bg-gray-50 border-t border-gray-100 text-center">
            <button onClick={() => onNavigate('strategy')} className="btn btn-primary text-sm w-full">Compare with My Strategy</button>
          </div>
        </section>
      </div>

      {/* Campaign Timing - Simplified Visual */}
      <section className="card bg-gray-900 text-white border-0">
        <div className="p-6">
          <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
            <BarChart2 size={18} className="text-pink-400" />
            Campaign Timing Intelligence
          </h3>
          <div className="relative pt-6 pb-12">
            <div className="h-1 bg-gray-700 w-full absolute top-1/2 transform -translate-y-1/2"></div>
            <div className="flex justify-between relative z-10">
              {["Oct 15", "Nov 1", "Dec 15", "Jan 15", "Feb 28 (Pred)"].map((date, i) => (
                <div key={i} className="flex flex-col items-center">
                  <div className={clsx("w-4 h-4 rounded-full border-4 border-gray-900", i === 4 ? "bg-pink-500 animate-pulse" : "bg-gray-500")}></div>
                  <span className="mt-4 text-xs font-medium text-gray-400">{date}</span>
                  {i === 4 && (
                    <div className="absolute top-[-80px] right-0 bg-pink-500/20 border border-pink-500/50 p-3 rounded text-xs w-48 backdrop-blur-sm">
                      <strong className="text-pink-300 block mb-1">AI Prediction (78%)</strong>
                      Next major campaign: Feb 25-Mar 5 (Holi). Est 25-30 ads.
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

const Stage4_Strategy = ({ onNavigate }) => {
  return (
    <div className="animate-fade-in space-y-8">
      <button onClick={() => onNavigate('deep_dive')} className="text-sm text-muted hover:text-primary flex items-center gap-1 mb-4">
        <ChevronRight size={16} className="rotate-180" /> Back to Analysis
      </button>
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Your Strategy vs Competitors</h1>
        <p className="text-muted text-lg mt-2">Side-by-side comparison</p>
      </header>

      <div className="card overflow-hidden mb-8">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="p-4 font-semibold text-muted text-xs uppercase tracking-wider">Metric</th>
              <th className="p-4 font-bold text-primary w-1/3">YOU (Bella Vita)</th>
              <th className="p-4 font-semibold w-1/3">Avg Competitor</th>
              <th className="p-4 font-semibold w-16"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {mockData.strategy.comparison.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                <td className="p-4 text-sm font-medium">{row.metric}</td>
                <td className="p-4 text-sm font-bold text-gray-800">{row.you}</td>
                <td className="p-4 text-sm text-gray-600">{row.comp}</td>
                <td className="p-4 text-center">
                  {row.status === 'danger' && <AlertTriangle size={16} className="text-red-500 inline" />}
                  {row.status === 'success' && <Check size={16} className="text-green-500 inline" />}
                  {row.status === 'neutral' && <div className="w-4 h-1 bg-gray-200 inline-block rounded"></div>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <section>
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2"><Zap size={20} className="text-indigo-600" /> AI Recommendations for You</h3>
        <div className="grid gap-4">
          {mockData.strategy.recommendations.map((rec, i) => (
            <div key={i} className="card p-5 border-l-4 border-l-indigo-500 flex flex-col md:flex-row gap-6 items-start">
              <div className="flex-1">
                <h4 className="font-bold text-lg text-gray-900 mb-1">{rec.title}</h4>
                <p className="text-sm text-muted mb-3">{rec.reason}</p>
                <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-3 py-1 rounded text-sm font-medium">
                  <TrendingUp size={14} /> Action: {rec.action}
                </div>
              </div>
              <div className="text-right min-w-[120px]">
                <span className="block text-xs font-bold text-muted uppercase">Expected Impact</span>
                <span className="text-lg font-bold text-green-600">{rec.impact}</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      <div className="flex justify-end gap-3 mt-8">
        <button className="btn btn-outline">Generate Action Plan</button>
        <button onClick={() => onNavigate('export')} className="btn btn-primary">Proceed to Export</button>
      </div>
    </div>
  )
}

const Stage5_Export = ({ onReset }) => {
  return (
    <div className="animate-fade-in max-w-2xl mx-auto py-12">
      <div className="text-center mb-10">
        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
          <Check size={32} />
        </div>
        <h1 className="text-3xl font-bold mb-2">Analysis Complete</h1>
        <p className="text-muted">Ready to share with your team?</p>
      </div>

      <div className="card mb-8">
        <div className="p-4 border-b border-gray-100 font-semibold bg-gray-50 flex items-center gap-2">
          <Download size={18} /> Export Options
        </div>
        <div className="p-2">
          {[
            { label: "Executive Summary (2 pages)", format: "PDF", icon: <Shield size={18} /> },
            { label: "Full Analysis Report (15 pages)", format: "PDF", icon: <BarChart2 size={18} /> },
            { label: "Data Tables", format: "CSV", icon: <BarChart size={18} /> },
            { label: "PowerPoint Deck", format: "PPTX", icon: <Share2 size={18} /> },
          ].map((opt, i) => (
            <div key={i} className="flex items-center p-4 hover:bg-gray-50 rounded-lg cursor-pointer group">
              <div className="w-10 h-10 rounded bg-gray-100 flex items-center justify-center text-gray-500 mr-4 group-hover:bg-white group-hover:shadow-sm transition-all">
                {opt.icon}
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{opt.label}</h4>
                <span className="text-xs text-muted">{opt.format}</span>
              </div>
              <button className="btn btn-outline py-1 px-3 text-xs">Download</button>
            </div>
          ))}
        </div>
      </div>

      <div className="card p-6 mb-8">
        <h4 className="font-semibold mb-4 flex items-center gap-2"><Bell size={18} /> Set up Alerts</h4>
        <div className="space-y-3">
          {[
            "Notify me when competitors launch new campaigns",
            "Weekly summary every Monday",
            "Alert when gap opportunities detected"
          ].map((label, i) => (
            <label key={i} className="flex items-center gap-3 cursor-pointer">
              <input type="checkbox" defaultChecked className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary" />
              <span className="text-gray-700">{label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="flex gap-4">
        <button onClick={onReset} className="btn btn-outline w-full">Start New Analysis</button>
        <button className="btn btn-primary w-full">Save Preferences & Exit</button>
      </div>
    </div>
  )
}

function App() {
  const [stage, setStage] = useState('onboarding'); // onboarding, dashboard, deep_dive, strategy, export

  const renderStage = () => {
    switch (stage) {
      case 'onboarding': return <Stage1_Onboarding onComplete={() => setStage('dashboard')} />;
      case 'dashboard': return <Stage2_Dashboard onNavigate={setStage} />;
      case 'deep_dive': return <Stage3_DeepDive onNavigate={setStage} />;
      case 'strategy': return <Stage4_Strategy onNavigate={setStage} />;
      case 'export': return <Stage5_Export onReset={() => setStage('onboarding')} />;
      default: return <Stage1_Onboarding onComplete={() => setStage('dashboard')} />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation / Header */}
      <nav className="h-16 border-b border-gray-100 flex items-center justify-between px-6 bg-white sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white font-bold">S</div>
          <span className="font-bold text-xl tracking-tight text-gray-900">StratScout</span>
        </div>
        <div className="hidden md:flex items-center gap-6 text-sm font-medium text-muted">
          <span className={clsx("cursor-pointer hover:text-primary transition-colors", stage !== 'onboarding' && "text-primary")}>Dashboard</span>
          <span className="cursor-pointer hover:text-gray-900 transition-colors">Competitors</span>
          <span className="cursor-pointer hover:text-gray-900 transition-colors">Reports</span>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-xs font-bold text-gray-600">
            BV
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={stage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
          >
            {renderStage()}
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
