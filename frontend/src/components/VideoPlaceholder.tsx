import type { Platform } from '../types';

interface Props {
  platform: Platform;
}

const PLATFORM_FEATURES: Record<string, string[]> = {
  youtube: ['YouTube Shorts generation', 'Full video creation with AI narration', 'Auto-generated B-roll', 'Subtitle overlay'],
  instagram: ['Reels with trending audio sync', 'Story video generation', 'Auto-captioned clips', 'Carousel video slides'],
  linkedin: ['Professional video posts', 'Thought leadership clips', 'Conference-style presentations', 'Data visualization videos'],
};

export function VideoPlaceholder({ platform }: Props) {
  const features = PLATFORM_FEATURES[platform] || [];

  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="w-20 h-20 rounded-full bg-zinc-800 flex items-center justify-center mb-6">
        <svg className="w-10 h-10 text-zinc-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      </div>

      <h3 className="text-xl font-semibold text-zinc-200 mb-2">Video Generation</h3>
      <p className="text-zinc-400 mb-6 max-w-md">
        Video generation pipeline is under development. This feature will include AI-powered video creation with natural speech synthesis.
      </p>

      <div className="text-left bg-zinc-800/50 border border-zinc-700 rounded-lg p-4 max-w-sm w-full">
        <h4 className="text-sm font-medium text-zinc-300 mb-3">Planned Features</h4>
        <ul className="space-y-2">
          {features.map((f, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-zinc-400">
              <div className="w-1.5 h-1.5 rounded-full bg-zinc-600" />
              {f}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
