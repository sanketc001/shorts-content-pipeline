import { useState } from 'react';
import { TextGenerator } from '../TextGenerator';
import { ImageGenerator } from '../ImageGenerator';
import { VideoPlaceholder } from '../VideoPlaceholder';
import type { ContentTab } from '../../types';

const TABS: { key: ContentTab; label: string }[] = [
  { key: 'text', label: 'Text Content' },
  { key: 'image', label: 'Thumbnails & Images' },
  { key: 'video', label: 'Video' },
];

export function YouTubePanel() {
  const [activeTab, setActiveTab] = useState<ContentTab>('text');

  return (
    <div>
      {/* Sub-tabs */}
      <div className="flex gap-1 mb-6 p-1 bg-zinc-800/50 rounded-lg w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.key
                ? 'bg-red-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Platform hint */}
      <div className="mb-4 p-3 bg-red-900/10 border border-red-900/20 rounded-lg">
        <p className="text-xs text-red-300/70">
          {activeTab === 'text' && 'Generate SEO-optimized titles, descriptions, tags, and scripts for your YouTube videos.'}
          {activeTab === 'image' && 'Create eye-catching thumbnails optimized for YouTube\'s display sizes.'}
          {activeTab === 'video' && 'AI-powered video generation coming soon.'}
        </p>
      </div>

      {/* Content */}
      {activeTab === 'text' && <TextGenerator platform="youtube" />}
      {activeTab === 'image' && <ImageGenerator platform="youtube" />}
      {activeTab === 'video' && <VideoPlaceholder platform="youtube" />}
    </div>
  );
}
