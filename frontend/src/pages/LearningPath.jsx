import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { profileAPI, topicsAPI } from '../services/api';

export default function LearningPath() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [pathData, setPathData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const profRes = await profileAPI.get();
      const p = profRes.data.profile;
      if (!p || !p.selected_subject_id) { navigate('/subjects'); return; }
      setProfile(p);
      const pathRes = await topicsAPI.learningPath(p.selected_subject_id);
      setPathData(pathRes.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;
  if (!pathData) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">No learning path found</div>;

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <Link to="/dashboard" className="text-indigo-400 hover:text-indigo-300 text-sm">&larr; Dashboard</Link>
            <h1 className="text-2xl font-bold text-white mt-1">Learning Path</h1>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-indigo-400">{pathData.progress_percent}%</p>
            <p className="text-sm text-slate-400">{pathData.completed}/{pathData.total_topics} completed</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full h-3 bg-slate-700 rounded-full mb-8 overflow-hidden">
          <div className="h-full bg-gradient-to-r from-indigo-600 to-purple-600 transition-all duration-500" style={{ width: `${pathData.progress_percent}%` }} />
        </div>

        {/* Topics */}
        <div className="space-y-4">
          {pathData.topics.map((topic, idx) => (
            <div key={topic.id} className={`rounded-xl border p-5 transition ${
              topic.status === 'completed' ? 'bg-emerald-500/10 border-emerald-500/30' :
              topic.status === 'current' ? 'bg-indigo-500/10 border-indigo-500/50 ring-1 ring-indigo-500/30' :
              'bg-slate-800 border-slate-700 opacity-60'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg ${
                    topic.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                    topic.status === 'current' ? 'bg-indigo-500/20 text-indigo-400' :
                    'bg-slate-700 text-slate-500'
                  }`}>
                    {topic.status === 'completed' ? '✓' : topic.status === 'current' ? '▶' : '🔒'}
                  </div>
                  <div>
                    <h3 className="text-white font-medium">{topic.name}</h3>
                    <p className="text-sm text-slate-400 capitalize">{topic.difficulty} difficulty</p>
                  </div>
                </div>
                {topic.status === 'current' && (
                  <Link to={`/learn/${topic.id}`} className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition">
                    Start Learning
                  </Link>
                )}
                {topic.status === 'completed' && (
                  <Link to={`/learn/${topic.id}`} className="px-5 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-medium transition">
                    Review
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
