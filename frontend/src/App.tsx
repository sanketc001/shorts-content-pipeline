import { useState } from 'react';
import { YouTubePanel } from './components/youtube/YouTubePanel';
import { InstagramPanel } from './components/instagram/InstagramPanel';
import { LinkedInPanel } from './components/linkedin/LinkedInPanel';
import { AccountConnect } from './components/AccountConnect';
import type { Platform } from './types';

const PLATFORMS: { key: Platform; label: string; color: string; activeColor: string }[] = [
  { key: 'youtube', label: 'YouTube', color: 'text-red-400', activeColor: 'bg-red-600 border-red-500' },
  { key: 'instagram', label: 'Instagram', color: 'text-pink-400', activeColor: 'bg-gradient-to-r from-purple-600 to-pink-500 border-purple-500' },
  { key: 'linkedin', label: 'LinkedIn', color: 'text-blue-400', activeColor: 'bg-blue-600 border-blue-500' },
];

function App() {
  const [activePlatform, setActivePlatform] = useState<Platform>('youtube');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex">
      {/* Sidebar */}
      {sidebarOpen && (
        <aside className="w-64 bg-zinc-900 border-r border-zinc-800 p-4 flex flex-col gap-6 shrink-0">
          <div>
            <h1 className="text-lg font-bold text-white mb-1">Content Studio</h1>
            <p className="text-xs text-zinc-500">AI-Powered Content Pipeline</p>
          </div>

          {/* Platform Navigation */}
          <nav className="space-y-1">
            <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-2">Platforms</h3>
            {PLATFORMS.map((p) => (
              <button
                key={p.key}
                onClick={() => setActivePlatform(p.key)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all text-left ${
                  activePlatform === p.key
                    ? `${p.activeColor} text-white border shadow-lg`
                    : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 border border-transparent'
                }`}
              >
                <PlatformIcon platform={p.key} />
                {p.label}
              </button>
            ))}
          </nav>

          {/* Account Connections */}
          <AccountConnect />

          {/* Settings Info */}
          <div className="mt-auto">
            <div className="p-3 bg-zinc-800/50 rounded-lg">
              <p className="text-xs text-zinc-500">
                Text: localhost:3000/v1<br />
                Image: Direct + ComfyUI
              </p>
            </div>
          </div>
        </aside>
      )}

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 border-b border-zinc-800 flex items-center px-4 gap-4 shrink-0">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-400 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Platform Tabs (horizontal) */}
          <div className="flex gap-1 p-1 bg-zinc-800/50 rounded-lg">
            {PLATFORMS.map((p) => (
              <button
                key={p.key}
                onClick={() => setActivePlatform(p.key)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${
                  activePlatform === p.key
                    ? 'bg-zinc-700 text-white'
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto">
            {activePlatform === 'youtube' && <YouTubePanel />}
            {activePlatform === 'instagram' && <InstagramPanel />}
            {activePlatform === 'linkedin' && <LinkedInPanel />}
          </div>
        </div>
      </main>
    </div>
  );
}

function PlatformIcon({ platform }: { platform: Platform }) {
  if (platform === 'youtube') {
    return (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
      </svg>
    );
  }
  if (platform === 'instagram') {
    return (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
      </svg>
    );
  }
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
    </svg>
  );
}

export default App;
