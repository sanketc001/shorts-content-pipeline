import { useState, useRef } from 'react';
import { useImageGen } from '../hooks/useImageGen';
import type { Platform, ImageBackend, DimensionPreset } from '../types';
import { PLATFORM_DIMENSIONS } from '../types';

interface Props {
  platform: Platform;
}

export function ImageGenerator({ platform }: Props) {
  const dimensions = PLATFORM_DIMENSIONS[platform];
  const [mode, setMode] = useState<'t2i' | 'i2i'>('t2i');
  const [prompt, setPrompt] = useState('');
  const [selectedDim, setSelectedDim] = useState<DimensionPreset>(dimensions[0]);
  const [backend, setBackend] = useState<ImageBackend>('comfyui');
  const [denoise, setDenoise] = useState(0.65);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const { imageUrl, isGenerating, error, generateT2i, generateI2i, clear } = useImageGen();

  const handleGenerate = () => {
    if (!prompt.trim()) return;
    if (mode === 't2i') {
      generateT2i(prompt, selectedDim.width, selectedDim.height, backend);
    } else if (uploadedFile) {
      generateI2i(prompt, uploadedFile, denoise, backend);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = () => setUploadPreview(reader.result as string);
      reader.readAsDataURL(file);
    }
  };

  const downloadImage = () => {
    if (!imageUrl) return;
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = `${platform}_${mode}_${Date.now()}.png`;
    a.click();
  };

  return (
    <div className="space-y-4">
      {/* Mode Toggle */}
      <div className="flex gap-2">
        <button
          onClick={() => setMode('t2i')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === 't2i'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
          }`}
        >
          Text to Image (Z-Image Turbo)
        </button>
        <button
          onClick={() => setMode('i2i')}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            mode === 'i2i'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
          }`}
        >
          Image to Image (Flux 2 Klein)
        </button>
      </div>

      {/* Dimension Presets (T2I only) */}
      {mode === 't2i' && (
        <div>
          <label className="block text-sm text-zinc-400 mb-2">Dimensions</label>
          <div className="flex flex-wrap gap-2">
            {dimensions.map((d) => (
              <button
                key={d.label}
                onClick={() => setSelectedDim(d)}
                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  selectedDim.label === d.label
                    ? 'bg-emerald-600 text-white'
                    : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
                }`}
              >
                {d.label} ({d.width}x{d.height})
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Image Upload (I2I only) */}
      {mode === 'i2i' && (
        <div className="space-y-3">
          <div>
            <label className="block text-sm text-zinc-400 mb-2">Source Image</label>
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-zinc-600 rounded-lg p-6 text-center cursor-pointer hover:border-zinc-500 transition-colors"
            >
              {uploadPreview ? (
                <img
                  src={uploadPreview}
                  alt="Upload preview"
                  className="max-h-48 mx-auto rounded"
                />
              ) : (
                <div className="text-zinc-500">Click to upload an image</div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm text-zinc-400 mb-1">
              Transformation Strength: {denoise.toFixed(2)}
            </label>
            <input
              type="range"
              min={0.1}
              max={1.0}
              step={0.05}
              value={denoise}
              onChange={(e) => setDenoise(parseFloat(e.target.value))}
              className="w-full accent-emerald-500"
            />
            <div className="flex justify-between text-xs text-zinc-500">
              <span>Subtle</span>
              <span>Strong</span>
            </div>
          </div>
        </div>
      )}

      {/* Prompt */}
      <div>
        <label className="block text-sm text-zinc-400 mb-1">
          {mode === 't2i' ? 'Image Prompt' : 'Transformation Prompt'}
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder={
            mode === 't2i'
              ? 'Describe the image you want to generate...'
              : 'Describe how to transform the uploaded image...'
          }
          rows={3}
          className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none"
        />
      </div>

      {/* Backend Selector */}
      <div>
        <label className="block text-sm text-zinc-400 mb-1">Backend</label>
        <div className="flex gap-2">
          <button
            onClick={() => setBackend('direct')}
            className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              backend === 'direct'
                ? 'bg-zinc-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            Direct (Faster)
          </button>
          <button
            onClick={() => setBackend('comfyui')}
            className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              backend === 'comfyui'
                ? 'bg-zinc-600 text-white'
                : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
            }`}
          >
            ComfyUI (Flexible)
          </button>
        </div>
      </div>

      {/* Generate Button */}
      <div className="flex gap-2">
        <button
          onClick={handleGenerate}
          disabled={isGenerating || !prompt.trim() || (mode === 'i2i' && !uploadedFile)}
          className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-zinc-700 disabled:text-zinc-500 text-white rounded-lg font-medium transition-colors"
        >
          {isGenerating ? 'Generating...' : 'Generate Image'}
        </button>
        {imageUrl && (
          <>
            <button
              onClick={downloadImage}
              className="px-6 py-3 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg font-medium transition-colors"
            >
              Download
            </button>
            <button
              onClick={clear}
              className="px-6 py-3 bg-zinc-700 hover:bg-zinc-600 text-white rounded-lg font-medium transition-colors"
            >
              Clear
            </button>
          </>
        )}
      </div>

      {/* Loading */}
      {isGenerating && (
        <div className="flex items-center gap-3 p-4 bg-zinc-800 border border-zinc-700 rounded-lg">
          <div className="w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-zinc-300 text-sm">Generating image...</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          {error}
        </div>
      )}

      {/* Result */}
      {imageUrl && (
        <div className="rounded-lg overflow-hidden border border-zinc-700">
          <img src={imageUrl} alt="Generated" className="w-full" />
        </div>
      )}
    </div>
  );
}
