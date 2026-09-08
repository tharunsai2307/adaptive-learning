import { Component } from 'react';

/**
 * Without this, any render-time exception unmounts the whole tree and the user
 * sees a blank page with no clue what happened (verified: a blocked
 * localStorage throws during AuthProvider's initial render and did exactly that).
 */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    console.error('AdaptiveLearn crashed:', error, info?.componentStack);
  }

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
        <div className="max-w-lg w-full bg-slate-800 border border-red-500/40 rounded-2xl p-8">
          <h1 className="text-xl font-bold text-white mb-2">Something went wrong</h1>
          <p className="text-slate-400 text-sm mb-4">
            The app hit an unexpected error. The details below help identify it.
          </p>
          <pre className="bg-slate-900 border border-slate-700 rounded-lg p-3 text-xs text-red-300 whitespace-pre-wrap break-words max-h-48 overflow-auto">
            {String(this.state.error?.message || this.state.error)}
          </pre>
          <button
            onClick={() => window.location.reload()}
            className="mt-6 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition"
          >
            Reload the app
          </button>
        </div>
      </div>
    );
  }
}
