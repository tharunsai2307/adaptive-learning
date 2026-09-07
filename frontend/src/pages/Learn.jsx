import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { topicsAPI, tutorAPI } from '../services/api';

export default function Learn() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [topic, setTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => { loadTopic(); }, [topicId]);
  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [chatMessages]);

  const loadTopic = async () => {
    try {
      const res = await topicsAPI.get(topicId);
      setTopic(res.data);
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const question = chatInput;
    setChatInput('');
    setChatMessages((prev) => [...prev, { role: 'user', content: question }]);
    setChatLoading(true);
    try {
      const res = await tutorAPI.ask(topicId, question);
      setChatMessages((prev) => [...prev, { role: 'tutor', content: res.data.answer }]);
    } catch (err) {
      setChatMessages((prev) => [...prev, { role: 'tutor', content: 'Sorry, I could not process your question right now.' }]);
    } finally { setChatLoading(false); }
  };

  if (loading) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Loading topic...</div>;
  if (!topic) return <div className="min-h-screen bg-slate-900 flex items-center justify-center text-white">Topic not found</div>;

  return (
    <div className="min-h-screen bg-slate-900">
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link to="/learning-path" className="text-indigo-400 hover:text-indigo-300 text-sm mb-1 inline-block">&larr; Back to Learning Path</Link>
            <h1 className="text-2xl font-bold text-white">{topic.name}</h1>
            <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-medium ${topic.difficulty === 'easy' ? 'bg-emerald-500/20 text-emerald-300' : topic.difficulty === 'medium' ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300'}`}>{topic.difficulty} difficulty</span>
          </div>
          <button onClick={() => navigate(`/quiz/${topicId}`)} className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition shadow-lg shadow-indigo-500/30">Take Quiz</button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Section title="Introduction">{topic.introduction}</Section>
            <Section title="Basic Explanation">{topic.explanation}</Section>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Section title="Basic Example" accent="amber">{topic.basic_example}</Section>
              <Section title="Advanced Example" accent="purple">{topic.advanced_example}</Section>
            </div>
            <Section title="Key Points">{topic.key_points}</Section>
            <Section title="Learning Resources">{topic.resources}</Section>
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 flex items-center gap-3">
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span className="text-slate-300">Recommended study time: <strong className="text-white">{topic.study_time_minutes} minutes</strong></span>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col h-[600px] sticky top-6">
            <div className="p-4 border-b border-slate-700 flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                <svg className="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>
              </div>
              <div><h3 className="text-white font-medium text-sm">AI Tutor</h3><p className="text-xs text-slate-400">Ask anything about this topic</p></div>
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.length === 0 && <div className="text-center py-8"><p className="text-slate-500 text-sm">Ask me anything about {topic.name}!</p></div>}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-xl px-4 py-3 text-sm ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-slate-700 text-slate-200'}`}>{msg.content}</div>
                </div>
              ))}
              {chatLoading && <div className="flex justify-start"><div className="bg-slate-700 rounded-xl px-4 py-3 text-sm text-slate-400">Thinking...</div></div>}
              <div ref={chatEndRef} />
            </div>
            <form onSubmit={handleAsk} className="p-4 border-t border-slate-700">
              <div className="flex gap-2">
                <input type="text" value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Ask a question..." className="flex-1 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500" />
                <button type="submit" disabled={chatLoading} className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition disabled:opacity-50">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function Section({ title, accent = 'indigo', children }) {
  const colors = { indigo: 'bg-indigo-500/20 text-indigo-400', amber: 'bg-amber-500/20 text-amber-400', purple: 'bg-purple-500/20 text-purple-400' };
  return (
    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${colors[accent]}`}>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <div className="text-slate-300 leading-relaxed whitespace-pre-line">{children}</div>
    </div>
  );
}
