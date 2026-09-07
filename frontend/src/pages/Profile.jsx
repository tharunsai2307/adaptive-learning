import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { profileAPI, getErrorMessage } from '../services/api';

const EDUCATIONS = ['B.Tech', 'B.Sc', 'BCA', 'MCA'];
const YEARS = ['1st Year', '2nd Year', '3rd Year', '4th Year'];

const DEPT_MAP = {
  'B.Tech': ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical'],
  'B.Sc': ['Computer Science', 'Physics', 'Chemistry', 'Mathematics'],
  'BCA': ['Computer Science', 'Information Technology'],
  'MCA': ['Computer Science', 'Information Technology', 'Data Science'],
};

export default function Profile() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ education: '', year: '', department: '' });
  const [existingProfile, setExistingProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    let isMounted = true;
    profileAPI
      .get()
      .then((res) => {
        if (isMounted && res.data?.profile) {
          setExistingProfile(res.data.profile);
          setForm({
            education: res.data.profile.education || '',
            year: res.data.profile.year || '',
            department: res.data.profile.department || '',
          });
        }
      })
      .catch((err) => {
        console.warn('Could not fetch existing profile:', err);
      })
      .finally(() => {
        if (isMounted) setFetching(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.education || !form.year || !form.department) {
      setError('Please select Education, Year, and Department');
      return;
    }
    setLoading(true);
    setError('');
    setSuccess('');
    try {
      await profileAPI.save(form);
      setSuccess('Profile saved successfully!');
      setTimeout(() => {
        navigate('/subjects');
      }, 500);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to save profile'));
    } finally {
      setLoading(false);
    }
  };

  const departments = form.education ? DEPT_MAP[form.education] || [] : [];

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col justify-between">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-600/30 flex items-center justify-center border border-indigo-500/30">
            <svg className="w-5 h-5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <span className="font-bold text-lg text-white">AdaptiveLearn</span>
        </div>

        <div className="flex items-center space-x-4 text-sm">
          {existingProfile && (
            <Link
              to="/subjects"
              className="text-indigo-400 hover:text-indigo-300 font-medium transition"
            >
              Browse Subjects &rarr;
            </Link>
          )}
          {user && (
            <span className="text-slate-400 hidden sm:inline">
              Signed in as <strong className="text-slate-200">{user.name || user.email}</strong>
            </span>
          )}
          <button
            onClick={() => {
              logout();
              navigate('/');
            }}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
          >
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center p-4 my-8">
        <div className="w-full max-w-lg">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-8 shadow-2xl">
            <div className="text-center mb-8">
              <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl bg-indigo-500/20 mb-4 border border-indigo-500/30">
                <svg className="w-7 h-7 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">
                {existingProfile ? 'Your Academic Profile' : 'Setup Student Profile'}
              </h2>
              <p className="text-slate-400 mt-1 text-sm">
                Customize your curriculum, recommended topics, and adaptive quizzes
              </p>
            </div>

            {error && (
              <div className="bg-red-500/20 border border-red-500/50 text-red-200 px-4 py-3 rounded-lg mb-4 text-sm flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError('')} className="text-red-300 hover:text-white ml-2">&times;</button>
              </div>
            )}

            {success && (
              <div className="bg-emerald-500/20 border border-emerald-500/50 text-emerald-200 px-4 py-3 rounded-lg mb-4 text-sm">
                {success}
              </div>
            )}

            {fetching ? (
              <div className="py-12 flex flex-col items-center justify-center space-y-3">
                <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm text-slate-400">Loading your profile details...</p>
              </div>
            ) : (
              <form onSubmit={handleSave} className="space-y-6">
                {/* Education */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">1. Education / Degree</label>
                  <div className="grid grid-cols-2 gap-2">
                    {EDUCATIONS.map((edu) => (
                      <button
                        key={edu}
                        type="button"
                        onClick={() => setForm({ ...form, education: edu, department: '' })}
                        className={`py-3 px-4 rounded-xl border text-sm font-medium transition duration-150 ${
                          form.education === edu
                            ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/30'
                            : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
                        }`}
                      >
                        {edu}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Year */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">2. Year of Study</label>
                  <div className="grid grid-cols-2 gap-2">
                    {YEARS.map((year) => (
                      <button
                        key={year}
                        type="button"
                        onClick={() => setForm({ ...form, year })}
                        className={`py-3 px-4 rounded-xl border text-sm font-medium transition duration-150 ${
                          form.year === year
                            ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/30'
                            : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
                        }`}
                      >
                        {year}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Department */}
                {form.education ? (
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">3. Department / Specialization</label>
                    <div className="grid grid-cols-2 gap-2">
                      {departments.map((dept) => (
                        <button
                          key={dept}
                          type="button"
                          onClick={() => setForm({ ...form, department: dept })}
                          className={`py-3 px-4 rounded-xl border text-sm font-medium transition duration-150 ${
                            form.department === dept
                              ? 'bg-indigo-600 border-indigo-500 text-white shadow-lg shadow-indigo-600/30'
                              : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:bg-slate-700 hover:text-white'
                          }`}
                        >
                          {dept}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-xl bg-slate-900/40 border border-slate-700/50 text-slate-400 text-xs text-center">
                    Select your degree above to view available departments.
                  </div>
                )}

                <div className="pt-2 flex flex-col sm:flex-row gap-3">
                  <button
                    type="submit"
                    disabled={loading || !form.education || !form.year || !form.department}
                    className="flex-1 py-3 px-6 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 text-white font-semibold rounded-xl transition duration-200 shadow-lg shadow-indigo-600/20 disabled:shadow-none disabled:text-slate-400 disabled:cursor-not-allowed text-center"
                  >
                    {loading ? 'Saving Profile...' : existingProfile ? 'Update & Continue' : 'Save Profile & Continue'}
                  </button>

                  {existingProfile && (
                    <Link
                      to="/subjects"
                      className="py-3 px-5 rounded-xl border border-slate-600 hover:bg-slate-700 text-slate-300 hover:text-white font-medium text-center transition"
                    >
                      Skip to Subjects
                    </Link>
                  )}
                </div>
              </form>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="text-center py-4 text-xs text-slate-500">
        AdaptiveLearn AI-Powered Personalization Engine
      </footer>
    </div>
  );
}
