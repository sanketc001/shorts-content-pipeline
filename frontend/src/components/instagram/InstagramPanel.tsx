import { useState } from 'react';
import { TextGenerator } from '../TextGenerator';
import { ImageGenerator } from '../ImageGenerator';
import { VideoPlaceholder } from '../VideoPlaceholder';
import type { ContentTab } from '../../types';

const TABS: { key: ContentTab; label: string }[] = [
  { key: 'text', label: 'Captions & Copy' },
  { key: 'image', label: 'Posts & Stories' },
  { key: 'video', label: 'Reels' },
];

export function InstagramPanel() {
  const [activeTab, setActiveTab] = useState<ContentTab>('text');

  return (
    <div>
      <div className="flex gap-1 mb-6 p-1 bg-zinc-800/50 rounded-lg w-fit">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
              activeTab === tab.key
                ? 'bg-gradient-to-r from-purple-600 to-pink-500 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mb-4 p-3 bg-purple-900/10 border border-purple-900/20 rounded-lg">
        <p className="text-xs text-purple-300/70">
          {activeTab === 'text' && 'Craft engaging captions, optimized hashtag sets, carousel plans, and reel scripts.'}
          {activeTab === 'image' && 'Generate square posts, portrait images, and story-sized visuals.'}
          {activeTab === 'video' && 'AI-powered Reels generation coming soon.'}
        </p>
      </div>

      {activeTab === 'text' && <TextGenerator platform="instagram" />}
      {activeTab === 'image' && <ImageGenerator platform="instagram" />}
      {activeTab === 'video' && <VideoPlaceholder platform="instagram" />}
    </div>
  );
}
