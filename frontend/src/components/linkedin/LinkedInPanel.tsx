import { useState } from 'react';
import { TextGenerator } from '../TextGenerator';
import { ImageGenerator } from '../ImageGenerator';
import { VideoPlaceholder } from '../VideoPlaceholder';
import type { ContentTab } from '../../types';

const TABS: { key: ContentTab; label: string }[] = [
  { key: 'text', label: 'Posts & Articles' },
  { key: 'image', label: 'Banners & Visuals' },
  { key: 'video', label: 'Video' },
];

export function LinkedInPanel() {
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
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="mb-4 p-3 bg-blue-900/10 border border-blue-900/20 rounded-lg">
        <p className="text-xs text-blue-300/70">
          {activeTab === 'text' && 'Write thought leadership posts, professional articles, and engagement-driving content.'}
          {activeTab === 'image' && 'Create professional banners and post visuals suited for LinkedIn.'}
          {activeTab === 'video' && 'AI-powered professional video content coming soon.'}
        </p>
      </div>

      {activeTab === 'text' && <TextGenerator platform="linkedin" />}
      {activeTab === 'image' && <ImageGenerator platform="linkedin" />}
      {activeTab === 'video' && <VideoPlaceholder platform="linkedin" />}
    </div>
  );
}
