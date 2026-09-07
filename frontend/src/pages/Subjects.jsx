import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileAPI, subjectsAPI } from '../services/api';

export default function Subjects() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const profRes = await profileAPI.get();
      const p = profRes.data.profile;
      if (!p) { navigate('/profile'); return; }
      setProfile(p);

      const subRes = await subjectsAPI.list(p.education, p.year, p.department);
      setSubjects(subRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const selectSubject = async (subjectId) => {
    await profileAPI.selectSubject(subjectId);
    navigate('/dashboard');
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading...</div>;

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">Select a Subject</h1>
          <p className="text-slate-400 mt-2">
            {profile?.education} — {profile?.year} — {profile?.department}
          </p>
        </div>

        {subjects.length === 0 ? (
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-12 text-center">
            <p className="text-slate-400 text-lg">No subjects available for your selection.</p>
            <p className="text-slate-500 text-sm mt-2">Try a different education/year/department combination.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {subjects.map((s) => (
              <button
                key={s.id}
                onClick={() => selectSubject(s.id)}
                className="bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-indigo-500 rounded-xl p-6 text-left transition duration-200 group"
              >
                <div className="w-12 h-12 rounded-lg bg-indigo-500/20 flex items-center justify-center mb-4 group-hover:bg-indigo-500/30 transition">
                  <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-white mb-1">{s.name}</h3>
                <p className="text-sm text-slate-400">{s.department}</p>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
