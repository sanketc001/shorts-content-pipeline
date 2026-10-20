import { useState } from 'react';
import { useTextStream } from '../hooks/useTextStream';
import type { Platform } from '../types';
import { PLATFORM_TEXT_TYPES, TEXT_MODELS } from '../types';

interface Props {
  platform: Platform;
}

export function TextGenerator({ platform }: Props) {
  const textTypes = PLATFORM_TEXT_TYPES[platform];
  const [contentType, setContentType] = useState(textTypes[0].value);
  const [topic, setTopic] = useState('');
  const [context, setContext] = useState('');
  const [tone, setTone] = useState('');
  const [model, setModel] = useState('gpt-4.1');
  const { output, isGenerating, error, generate, stop, clear } = useTextStream();

  const handleGenerate = () => {
    if (!topic.trim()) return;
    generate({
      platform,
      content_type: contentType,
      topic,
      context,
      tone,
      model,
    });
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(output);
  };

  return (
    <div className="space-y-4">
      {/* Content Type Selector */}
      <div className="flex flex-wrap gap-2">
        {textTypes.map((t) => (
          <button
            key={t.value}
            onClick={() => setContentType(t.value)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              contentType === t.value
                ? 'bg-indigo-600 text-white shadow-md'
                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Inputs */}
      <div className="space-y-3">
        <div>
          <label className="block text-sm text-zinc-400 mb-1">Topic / Subject</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="What is your content about?"
            className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm text-zinc-400 mb-1">Additional Context (optional)</label>
          <textarea
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Target audience, key points, specific requirements..."
            rows={3}
            className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none resize-none"
          />
        </div>

        <div className="flex gap-3">
          <div className="flex-1">
            <label className="block text-sm text-zinc-400 mb-1">Tone</label>
            <select
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:border-indigo-500 outline-none"
            >
              <option value="">Auto (platform default)</option>
              <option value="professional">Professional</option>
              <option value="casual">Casual</option>
              <option value="energetic">Energetic</option>
              <option value="educational">Educational</option>
              <option value="humorous">Humorous</option>
              <option value="inspirational">Inspirational</option>
            </select>
          </div>

          <div className="flex-1">
            <label className="block text-sm text-zinc-400 mb-1">Model</label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white focus:border-indigo-500 outline-none"
            >
              {TEXT_MODELS.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex gap-2">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !topic.trim()}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-lg font-medium transition-colors"
        >
          {isGenerating ? 'Generating...' : 'Generate'}
        </button>
        {isGenerating && (
          <button
            onClick={stop}
            className="px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors"
          >
            Stop
          </button>
        )}
        {output && !isGenerating && (
          <button
            onClick={clear}
            className="px-6 py-3 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg font-medium transition-colors"
          >
            Clear
          </button>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {/* Output */}
      {output && (
        <div className="relative">
          <div className="p-4 bg-zinc-800 border border-zinc-700 rounded-lg">
            <pre className="whitespace-pre-wrap text-zinc-200 text-sm leading-relaxed font-sans">
              {output}
              {isGenerating && <span className="animate-pulse">|</span>}
            </pre>
          </div>
          <button
            onClick={copyToClipboard}
            className="absolute top-3 right-3 p-2 bg-zinc-700 hover:bg-zinc-600 rounded-md text-zinc-300 text-xs transition-colors"
            title="Copy to clipboard"
          >
            Copy
          </button>
        </div>
      )}
    </div>
  );
}
