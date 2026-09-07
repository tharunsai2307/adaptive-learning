import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../services/api';

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.performanceHistory()
      .then(res => setHistory(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <Link to="/dashboard" className="text-indigo-400 hover:text-indigo-300 text-sm">&larr; Dashboard</Link>
          <h1 className="text-2xl font-bold text-white mt-1">Performance History</h1>
          <p className="text-slate-400 mt-1">Track your learning progress over time</p>
        </div>

        {history.length === 0 ? (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center">
            <p className="text-slate-400 text-lg">No quiz attempts yet</p>
            <p className="text-slate-500 text-sm mt-2">Complete a quiz to see your history here</p>
            <Link to="/learning-path" className="inline-block mt-4 px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition">
              Start Learning
            </Link>
          </div>
        ) : (
          <div className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-700/50">
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">#</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Date</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Topic</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Score</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Accuracy</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Time</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">Performance</th>
                    <th className="text-left py-4 px-5 text-slate-400 font-medium">RL Action</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((h, i) => (
                    <tr key={h.id || i} className="border-t border-slate-700/50 hover:bg-slate-700/30 transition">
                      <td className="py-4 px-5 text-slate-400">{i + 1}</td>
                      <td className="py-4 px-5 text-slate-300">{h.date ? new Date(h.date).toLocaleDateString() : '-'}</td>
                      <td className="py-4 px-5 text-white font-medium">{h.topic}</td>
                      <td className="py-4 px-5 text-slate-300">{h.score}/{h.total}</td>
                      <td className="py-4 px-5">
                        <span className={`font-medium ${h.accuracy >= 80 ? 'text-emerald-400' : h.accuracy >= 60 ? 'text-amber-400' : 'text-red-400'}`}>
                          {h.accuracy}%
                        </span>
                      </td>
                      <td className="py-4 px-5 text-slate-300">
                        {Math.floor(h.time_taken / 60)}m {h.time_taken % 60}s
                      </td>
                      <td className="py-4 px-5">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                          h.performance === 'Excellent' ? 'bg-emerald-500/20 text-emerald-300' :
                          h.performance === 'Average' ? 'bg-amber-500/20 text-amber-300' :
                          'bg-red-500/20 text-red-300'
                        }`}>{h.performance}</span>
                      </td>
                      <td className="py-4 px-5">
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-indigo-500/20 text-indigo-300">{h.rl_action}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
