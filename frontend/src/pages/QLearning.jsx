import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { qlearningAPI } from '../services/api';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

export default function QLearning() {
  const [qTable, setQTable] = useState(null);
  const [lastDecision, setLastDecision] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [tableRes, decisionRes] = await Promise.all([
        qlearningAPI.qTable(),
        qlearningAPI.lastDecision(),
      ]);
      setQTable(tableRes.data);
      setLastDecision(decisionRes.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading Q-Learning data...</div>;

  const actionColors = {
    REVISION: '#ef4444',
    PRACTICE: '#f59e0b',
    CONTINUE: '#10b981',
    ADVANCED: '#6366f1',
  };

  // Chart for current state Q-values
  const chartData = lastDecision?.q_values ? {
    labels: Object.keys(lastDecision.q_values),
    datasets: [{
      label: 'Q-Values',
      data: Object.values(lastDecision.q_values),
      backgroundColor: Object.keys(lastDecision.q_values).map(a => actionColors[a] || '#6366f1'),
      borderRadius: 8,
    }],
  } : null;

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <Link to="/dashboard" className="text-indigo-400 hover:text-indigo-300 text-sm">&larr; Dashboard</Link>
          <h1 className="text-2xl font-bold text-white mt-1">How AI Decides Your Next Lesson</h1>
          <p className="text-slate-400 mt-1">Visualizing the Q-Learning reinforcement learning process</p>
        </div>

        {/* Flow Visualization */}
        {lastDecision && !lastDecision.message && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-8 mb-8">
            <h2 className="text-lg font-semibold text-white mb-6 text-center">Q-Learning Decision Pipeline</h2>
            <div className="flex flex-col items-center space-y-4">
              {/* Step 1: Performance */}
              <FlowStep label="Student Performance" color="blue">
                <p>Accuracy: {lastDecision.accuracy}%</p>
                <p>Score: {lastDecision.score}/{lastDecision.total}</p>
              </FlowStep>
              <Arrow />
              {/* Step 2: State */}
              <FlowStep label="Current State" color="purple">
                <p className="text-xl font-bold">{lastDecision.current_state}</p>
                <p className="text-sm opacity-75">{lastDecision.performance_level} + {lastDecision.learning_speed}</p>
              </FlowStep>
              <Arrow />
              {/* Step 3: Q-Learning */}
              <FlowStep label="Q-Learning Agent" color="indigo">
                <p className="text-lg font-bold">Epsilon-Greedy Action Selection</p>
                <p className="text-sm opacity-75">Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]</p>
              </FlowStep>
              <Arrow />
              {/* Step 4: Actions */}
              <FlowStep label="Possible Actions" color="slate">
                <div className="flex gap-3">
                  {['REVISION', 'PRACTICE', 'CONTINUE', 'ADVANCED'].map(a => (
                    <span key={a} className={`px-3 py-1 rounded-full text-xs font-bold ${a === lastDecision.chosen_action ? 'ring-2 ring-white' : 'opacity-50'}`} style={{ backgroundColor: actionColors[a] + '33', color: actionColors[a] }}>
                      {a}
                    </span>
                  ))}
                </div>
              </FlowStep>
              <Arrow />
              {/* Step 5: Selected */}
              <FlowStep label="Selected Action" color="green">
                <p className="text-xl font-bold" style={{ color: actionColors[lastDecision.chosen_action] }}>{lastDecision.chosen_action}</p>
              </FlowStep>
              <Arrow />
              {/* Step 6: Recommendation */}
              <FlowStep label="Recommendation" color="amber">
                <p className="font-medium">
                  {lastDecision.chosen_action === 'REVISION' && 'Repeat topic with simpler explanation'}
                  {lastDecision.chosen_action === 'PRACTICE' && 'Additional practice exercises recommended'}
                  {lastDecision.chosen_action === 'CONTINUE' && 'Move to the next topic'}
                  {lastDecision.chosen_action === 'ADVANCED' && 'Skip to advanced material'}
                </p>
              </FlowStep>
            </div>
          </div>
        )}

        {!lastDecision?.current_state && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center mb-8">
            <p className="text-slate-400 text-lg">{lastDecision?.message || 'Complete a quiz to see Q-Learning in action!'}</p>
          </div>
        )}

        {/* Q-Values Chart */}
        {chartData && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-8">
            <h3 className="text-lg font-semibold text-white mb-4">Q-Values for Current State</h3>
            <div className="max-w-md mx-auto">
              <Bar data={chartData} options={{
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                  y: { ticks: { color: '#94a3b8' }, grid: { color: '#334155' } },
                  x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
                },
              }} />
            </div>
          </div>
        )}

        {/* Full Q-Table */}
        {qTable && (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Complete Q-Table</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">State</th>
                    {qTable.actions.map(a => (
                      <th key={a} className="text-center py-3 px-4 font-medium" style={{ color: actionColors[a] }}>{a}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {qTable.states.map(state => (
                    <tr key={state} className={`border-b border-slate-700/50 ${lastDecision?.current_state === state ? 'bg-indigo-500/10' : ''}`}>
                      <td className="py-3 px-4 text-white font-medium">
                        {state}
                        {lastDecision?.current_state === state && <span className="ml-2 text-xs text-indigo-400">(current)</span>}
                      </td>
                      {qTable.actions.map(action => {
                        const val = qTable.table[state]?.[action] ?? 0;
                        return (
                          <td key={action} className="text-center py-3 px-4">
                            <span className={`font-mono ${val > 0 ? 'text-emerald-400' : val < 0 ? 'text-red-400' : 'text-slate-400'}`}>
                              {val.toFixed(4)}
                            </span>
                          </td>
                        );
                      })}
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

function FlowStep({ label, color, children }) {
  const colors = {
    blue: 'border-blue-500/50 bg-blue-500/10',
    purple: 'border-purple-500/50 bg-purple-500/10',
    indigo: 'border-indigo-500/50 bg-indigo-500/10',
    slate: 'border-slate-500/50 bg-slate-700/50',
    green: 'border-emerald-500/50 bg-emerald-500/10',
    amber: 'border-amber-500/50 bg-amber-500/10',
  };
  return (
    <div className={`w-full max-w-lg border rounded-xl p-4 text-center ${colors[color]}`}>
      <p className="text-xs text-slate-400 uppercase tracking-wider mb-2">{label}</p>
      <div className="text-white">{children}</div>
    </div>
  );
}

function Arrow() {
  return (
    <svg className="w-6 h-6 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
    </svg>
  );
}
