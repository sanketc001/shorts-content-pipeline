import { useState, useEffect } from 'react';
import { getAuthStatus } from '../api/client';
import type { AuthStatus, Platform } from '../types';

const PLATFORM_INFO: Record<Platform, { name: string; color: string; icon: string }> = {
  youtube: { name: 'YouTube', color: 'bg-red-600 hover:bg-red-700', icon: 'YT' },
  instagram: { name: 'Instagram', color: 'bg-gradient-to-r from-purple-600 to-pink-500 hover:from-purple-700 hover:to-pink-600', icon: 'IG' },
  linkedin: { name: 'LinkedIn', color: 'bg-blue-600 hover:bg-blue-700', icon: 'LI' },
};

export function AccountConnect() {
  const [status, setStatus] = useState<AuthStatus>({ youtube: false, instagram: false, linkedin: false });
  const [backendOnline, setBackendOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuthStatus()
      .then((s) => {
        setStatus(s);
        setBackendOnline(true);
      })
      .catch(() => setBackendOnline(false))
      .finally(() => setLoading(false));

    // Check for auth callback result
    const params = new URLSearchParams(window.location.search);
    const success = params.get('auth_success');
    const error = params.get('auth_error');
    if (success || error) {
      window.history.replaceState({}, '', window.location.pathname);
      if (success) {
        getAuthStatus().then(setStatus).catch(() => {});
      }
    }
  }, []);

  const connect = (platform: Platform) => {
    window.location.href = `/api/auth/${platform}/login`;
  };

  const disconnect = async (platform: Platform) => {
    await fetch(`/api/auth/${platform}/disconnect`, { method: 'POST' });
    setStatus((prev) => ({ ...prev, [platform]: false }));
  };

  if (loading) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-xs font-medium text-zinc-500 uppercase tracking-wider mb-3">Connected Accounts</h3>
      {!backendOnline && (
        <div className="p-2 rounded-lg bg-yellow-900/20 border border-yellow-800/30">
          <p className="text-xs text-yellow-400/70">Backend offline. Start the server to connect accounts.</p>
        </div>
      )}
      {(Object.keys(PLATFORM_INFO) as Platform[]).map((platform) => {
        const info = PLATFORM_INFO[platform];
        const connected = status[platform];

        return (
          <div
            key={platform}
            className="flex items-center justify-between p-2 rounded-lg bg-zinc-800/50"
          >
            <div className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-md flex items-center justify-center text-white text-xs font-bold ${info.color}`}>
                {info.icon}
              </div>
              <span className="text-sm text-zinc-300">{info.name}</span>
            </div>
            {connected ? (
              <button
                onClick={() => disconnect(platform)}
                className="text-xs text-zinc-500 hover:text-red-400 transition-colors"
              >
                Disconnect
              </button>
            ) : (
              <button
                onClick={() => connect(platform)}
                disabled={!backendOnline}
                className="text-xs text-indigo-400 hover:text-indigo-300 disabled:text-zinc-600 disabled:cursor-not-allowed transition-colors"
              >
                Connect
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
