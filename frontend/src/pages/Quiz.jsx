import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { quizAPI, topicsAPI } from '../services/api';

export default function Quiz() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [startTime] = useState(Date.now());

  useEffect(() => { loadData(); }, [topicId]);

  const loadData = async () => {
    try {
      const [topicRes, qRes] = await Promise.all([
        topicsAPI.get(topicId),
        quizAPI.questions(topicId),
      ]);
      setTopic(topicRes.data);
      setQuestions(qRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    const timeTaken = Math.floor((Date.now() - startTime) / 1000);
    try {
      const res = await quizAPI.submit({
        topic_id: parseInt(topicId),
        answers,
        time_taken_seconds: timeTaken,
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}m ${s}s`;
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading quiz...</div>;

  // Results view
  if (result) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-8">
            <div className={`inline-flex items-center justify-center w-20 h-20 rounded-full mb-4 ${
              result.performance_level === 'Excellent' ? 'bg-emerald-500/20' :
              result.performance_level === 'Average' ? 'bg-amber-500/20' : 'bg-red-500/20'
            }`}>
              <span className="text-4xl">{result.performance_level === 'Excellent' ? '🏆' : result.performance_level === 'Average' ? '👍' : '📚'}</span>
            </div>
            <h1 className="text-3xl font-bold text-white">Quiz Complete!</h1>
            <p className="text-slate-400 mt-2">{topic?.name}</p>
          </div>

          {/* Score Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
              <p className="text-3xl font-bold text-white">{result.score}/{result.total_questions}</p>
              <p className="text-sm text-slate-400 mt-1">Score</p>
            </div>
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
              <p className="text-3xl font-bold text-white">{result.accuracy}%</p>
              <p className="text-sm text-slate-400 mt-1">Accuracy</p>
            </div>
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
              <p className="text-3xl font-bold text-white">{formatTime(result.time_taken_seconds)}</p>
              <p className="text-sm text-slate-400 mt-1">Time Taken</p>
            </div>
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 text-center">
              <span className={`text-2xl font-bold ${
                result.performance_level === 'Excellent' ? 'text-emerald-400' :
                result.performance_level === 'Average' ? 'text-amber-400' : 'text-red-400'
              }`}>{result.performance_level}</span>
              <p className="text-sm text-slate-400 mt-1">Performance</p>
            </div>
          </div>

          {/* Q-Learning Result */}
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 mb-6">
            <h3 className="text-lg font-semibold text-white mb-4">Q-Learning Decision</h3>
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-indigo-500/20 rounded-lg px-4 py-2">
                <p className="text-sm text-indigo-300">State</p>
                <p className="text-white font-bold">{result.q_learning_viz.current_state}</p>
              </div>
              <div className="text-slate-500">→</div>
              <div className="bg-emerald-500/20 rounded-lg px-4 py-2">
                <p className="text-sm text-emerald-300">Action</p>
                <p className="text-white font-bold">{result.rl_action}</p>
              </div>
              <div className="text-slate-500">→</div>
              <div className="bg-amber-500/20 rounded-lg px-4 py-2">
                <p className="text-sm text-amber-300">Reward</p>
                <p className="text-white font-bold">{result.q_learning_viz.reward > 0 ? '+' : ''}{result.q_learning_viz.reward}</p>
              </div>
            </div>
            <div className="bg-indigo-500/10 border border-indigo-500/30 rounded-lg p-4">
              <p className="text-indigo-300 font-medium">{result.recommendation.title}</p>
              <p className="text-slate-300 text-sm mt-1">{result.recommendation.message}</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 justify-center">
            <Link to="/dashboard" className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition">
              Back to Dashboard
            </Link>
            <Link to="/learning-path" className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition">
              Continue Learning
            </Link>
            <Link to="/qlearning" className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition">
              View Q-Learning Viz
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Quiz view
  const answeredCount = Object.keys(answers).length;

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link to={`/learn/${topicId}`} className="text-indigo-400 hover:text-indigo-300 text-sm">&larr; Back to Topic</Link>
            <h1 className="text-2xl font-bold text-white mt-1">{topic?.name} — Quiz</h1>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-400">{answeredCount}/{questions.length} answered</span>
            <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-600 transition-all" style={{ width: `${(answeredCount / Math.max(questions.length, 1)) * 100}%` }} />
            </div>
          </div>
        </div>

        {/* Questions */}
        <div className="space-y-6">
          {questions.map((q, idx) => (
            <div key={q.id} className="bg-slate-800 rounded-xl border border-slate-700 p-6">
              <p className="text-white font-medium mb-4">
                <span className="text-indigo-400 mr-2">Q{idx + 1}.</span>
                {q.question}
              </p>
              <div className="space-y-2">
                {['A', 'B', 'C', 'D'].map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setAnswers({ ...answers, [q.id]: opt })}
                    className={`w-full text-left px-4 py-3 rounded-lg border transition ${
                      answers[q.id] === opt
                        ? 'bg-indigo-600/20 border-indigo-500 text-white'
                        : 'bg-slate-700/50 border-slate-600 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    <span className="font-medium mr-3">{opt}.</span>
                    {q[`option_${opt.toLowerCase()}`]}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Submit */}
        <div className="mt-8 text-center">
          <button
            onClick={handleSubmit}
            disabled={submitting || answeredCount === 0}
            className="px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold text-lg transition shadow-lg shadow-indigo-500/30 disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Quiz'}
          </button>
        </div>
      </div>
    </div>
  );
}
