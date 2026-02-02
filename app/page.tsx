"use client";

import { useState } from 'react';

export default function Home() {
  const [review, setReview] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Modal states
  const [isPreferencesOpen, setIsPreferencesOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  // Preferences states
  const [enableAnimations, setEnableAnimations] = useState(true);
  const [highContrast, setHighContrast] = useState(false);

  const analyzeSentiment = async () => {
    if (!review.trim()) return;
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze sentiment. Ensure the API is running.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError('An error occurred. Please make sure the backend API is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setReview('');
    setResult(null);
    setError('');
  };

  return (
    <div className={`min-h-screen flex flex-col items-center justify-center p-4 text-white overflow-hidden relative ${enableAnimations ? 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 animate-gradient' : 'bg-slate-900'
      }`}>

      {/* Background Overlay */}
      <div className={`absolute inset-0 bg-black/20 pointer-events-none ${highContrast ? 'opacity-90 bg-black' : ''}`}></div>

      {/* Navigation Bar */}
      <nav className="fixed top-0 left-0 right-0 z-50 p-6 flex justify-between items-center bg-black/10 backdrop-blur-sm border-b border-white/5">
        <div className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-pink-400">
          SentimentAI
        </div>
        <div className="flex gap-4">
          <button
            onClick={() => setIsAboutOpen(true)}
            className="p-2 rounded-full hover:bg-white/10 transition text-gray-300 hover:text-white"
            title="About Project"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </button>
          <button
            onClick={() => setIsPreferencesOpen(true)}
            className="p-2 rounded-full hover:bg-white/10 transition text-gray-300 hover:text-white"
            title="Preferences"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 w-full max-w-3xl flex flex-col items-center mt-20">

        {/* Header */}
        <header className="mb-8 text-center animate-fade-in">
          <h1 className="text-5xl font-extrabold mb-2 bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-pink-400 drop-shadow-sm">
            Flipkart Sentiment Analysis
          </h1>
          <p className="text-lg text-gray-300 font-light">
            AI-Powered Insights for Product Reviews
          </p>
        </header>

        {/* Main Card */}
        <main className={`w-full bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl shadow-2xl overflow-hidden p-8 transition-all duration-300 hover:shadow-purple-500/20 ${enableAnimations ? 'animate-fade-in' : ''}`}>

          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <label htmlFor="review" className="block text-sm font-semibold text-gray-300 uppercase tracking-wide">
                Product Review
              </label>
              {review && (
                <button
                  onClick={handleReset}
                  className="text-xs text-gray-400 hover:text-white transition"
                >
                  Clear
                </button>
              )}
            </div>
            <textarea
              id="review"
              rows={4}
              className="w-full p-4 bg-black/20 border border-white/10 rounded-xl focus:ring-2 focus:ring-purple-500 focus:outline-none transition text-white placeholder-gray-400 resize-none shadow-inner"
              placeholder="Paste a review here to analyze its sentiment... (e.g. 'Quality is superb')"
              value={review}
              onChange={(e) => setReview(e.target.value)}
            />
          </div>

          <button
            onClick={analyzeSentiment}
            disabled={loading || !review.trim()}
            className={`w-full py-4 px-6 text-lg font-bold rounded-xl transition-all transform duration-200 ${loading || !review.trim()
              ? 'bg-gray-600/50 cursor-not-allowed opacity-50'
              : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 hover:scale-[1.02] shadow-lg shadow-purple-500/30'
              }`}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
                Analyzing...
              </span>
            ) : (
              'Analyze Sentiment'
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 text-red-200 rounded-lg animate-fade-in flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {error}
            </div>
          )}

          {/* Results Section */}
          {result && (
            <div className={`mt-8 ${enableAnimations ? 'animate-fade-in' : ''}`}>
              <div className="border-t border-white/10 pt-6">
                <h2 className="text-xl font-semibold mb-4 text-white">Analysis Result</h2>

                <div className={`p-6 rounded-xl border-l-4 shadow-lg backdrop-blur-md transition-colors ${result.sentiment === 'Positive'
                  ? 'bg-green-500/10 border-green-500'
                  : 'bg-red-500/10 border-red-500'
                  }`}>
                  <div className="flex items-center justify-between mb-3">
                    <span className={`text-3xl font-extrabold tracking-tight ${result.sentiment === 'Positive' ? 'text-green-400' : 'text-red-400'
                      }`}>
                      {result.sentiment}
                    </span>
                    <div className="flex items-center gap-2 bg-black/20 px-3 py-1 rounded-full">
                      <span className="text-xs text-gray-400 uppercase font-semibold">Confidence</span>
                      <span className="text-sm font-bold text-white">{(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>

                  <p className="text-gray-300 text-sm leading-relaxed">
                    {result.sentiment === 'Positive'
                      ? 'This review reflects a high level of satisfaction with the product.'
                      : 'The customer seems dissatisfied. Check the identified pain points below.'}
                  </p>
                </div>

                {/* Pain Points */}
                {result.pain_points && result.pain_points.length > 0 && (
                  <div className="mt-6">
                    <h3 className="text-sm font-semibold text-gray-400 mb-3 uppercase tracking-wider">
                      Detected Pain Points
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {result.pain_points.map((point: string, index: number) => (
                        <span
                          key={index}
                          className="px-4 py-1.5 bg-red-500/20 text-red-200 rounded-full text-sm font-medium border border-red-500/30 shadow-sm flex items-center gap-1"
                        >
                          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
                          {point}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className={`mt-12 text-center relative z-10 delay-150 ${enableAnimations ? 'animate-fade-in' : ''}`}>
          <p className="text-sm font-medium text-gray-400">
            Powered by <span className="text-purple-400 hover:text-purple-300 transition-colors cursor-pointer">Karthik Vana</span>
          </p>
          <p className="text-xs text-gray-500 mt-1 uppercase tracking-widest">
            Data Engineer | ML Engineer | AI Engineer
          </p>
        </footer>
      </div>

      {/* Preferences Modal */}
      {isPreferencesOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-slate-900 border border-white/10 p-6 rounded-2xl shadow-2xl max-w-sm w-full">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Preferences</h2>
              <button
                onClick={() => setIsPreferencesOpen(false)}
                className="text-gray-400 hover:text-white"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-200">Enable Animations</span>
                <button
                  onClick={() => setEnableAnimations(!enableAnimations)}
                  className={`w-12 h-6 rounded-full p-1 transition-colors ${enableAnimations ? 'bg-blue-600' : 'bg-gray-600'}`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full transition-transform ${enableAnimations ? 'translate-x-6' : 'translate-x-0'}`}></div>
                </button>
              </div>

              <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <span className="text-gray-200">High Contrast</span>
                <button
                  onClick={() => setHighContrast(!highContrast)}
                  className={`w-12 h-6 rounded-full p-1 transition-colors ${highContrast ? 'bg-blue-600' : 'bg-gray-600'}`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full transition-transform ${highContrast ? 'translate-x-6' : 'translate-x-0'}`}></div>
                </button>
              </div>

              <button
                onClick={() => { handleReset(); setIsPreferencesOpen(false); }}
                className="w-full py-2 bg-red-500/20 text-red-300 border border-red-500/30 rounded-lg hover:bg-red-500/30 transition mt-4 font-medium"
              >
                Reset Application
              </button>
            </div>
          </div>
        </div>
      )}

      {/* About Modal */}
      {isAboutOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fade-in">
          <div className="relative bg-slate-900 border border-white/10 p-1 rounded-3xl shadow-2xl max-w-xl w-full mx-4 overflow-hidden group">

            {/* Gradient Border Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 opacity-20 blur-xl group-hover:opacity-30 transition duration-500"></div>

            <div className="relative bg-slate-900/90 backdrop-blur-xl rounded-[22px] p-8 h-full">
              <div className="flex justify-between items-start mb-8">
                <div>
                  <h2 className="text-3xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400">
                    About SentimentAI
                  </h2>
                  <p className="text-sm text-gray-400 mt-1 font-medium tracking-wide">AI-POWERED ANALYTICS</p>
                </div>
                <button
                  onClick={() => setIsAboutOpen(false)}
                  className="p-2 -mr-2 -mt-2 text-gray-400 hover:text-white bg-white/5 hover:bg-white/10 rounded-full transition-all"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
              </div>

              <div className="space-y-8">
                <p className="text-base text-gray-300 leading-relaxed font-light">
                  Experience real-time sentiment analysis specifically tuned for Flipkart product reviews. Our AI instantly classifies feedback as <span className="text-green-400 font-semibold">Positive</span> or <span className="text-red-400 font-semibold">Negative</span> and intelligently extracts <span className="text-red-300 border-b border-red-300/30">critical pain points</span> to help you understand customer dissatisfaction at a glance.
                </p>

                <div className="space-y-2">
                  <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest pl-1">Developer Links</h3>
                  <div className="grid gap-3">
                    <a
                      href="https://portfolio-v-smoky.vercel.app/"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-900/40 to-blue-900/40 border border-white/5 hover:border-purple-500/50 rounded-xl group transition-all hover:shadow-lg hover:shadow-purple-500/10"
                    >
                      <div className="flex items-center gap-4">
                        <div className="p-2.5 bg-black/40 rounded-lg text-purple-300 ring-1 ring-white/10 group-hover:ring-purple-500/50 transition-all">
                          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
                        </div>
                        <div>
                          <p className="font-bold text-white text-base group-hover:text-purple-300 transition-colors">Portfolio</p>
                          <p className="text-xs text-gray-400">View my projects & case studies</p>
                        </div>
                      </div>
                      <svg className="w-5 h-5 text-gray-600 group-hover:text-white transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                    </a>

                    <div className="grid grid-cols-2 gap-3">
                      <a
                        href="https://github.com/karthik-vana"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex flex-col p-4 bg-white/5 hover:bg-white/10 border border-white/5 rounded-xl group transition-all"
                      >
                        <div className="mb-3 text-gray-300 group-hover:text-white transition-colors">
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd"></path></svg>
                        </div>
                        <p className="font-bold text-white text-sm">GitHub</p>
                        <p className="text-xs text-gray-500 mt-1 group-hover:text-gray-400">Explore Code</p>
                      </a>

                      <a
                        href="https://www.linkedin.com/in/karthik-vana/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex flex-col p-4 bg-white/5 hover:bg-[#0077b5]/20 border border-white/5 hover:border-[#0077b5]/30 rounded-xl group transition-all"
                      >
                        <div className="mb-3 text-[#0077b5] group-hover:text-blue-300 transition-colors">
                          <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z" /></svg>
                        </div>
                        <p className="font-bold text-white text-sm">LinkedIn</p>
                        <p className="text-xs text-gray-500 mt-1 group-hover:text-blue-200/70">Connect</p>
                      </a>
                    </div>
                  </div>
                </div>
              </div>

              <div className="absolute bottom-4 left-0 right-0 text-center">
                <p className="text-[10px] uppercase tracking-widest text-gray-600 font-semibold">Karthik Vana • Data • ML • AI</p>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
