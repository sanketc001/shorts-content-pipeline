export type Platform = 'youtube' | 'instagram' | 'linkedin';
export type ContentTab = 'text' | 'image' | 'video';
export type ImageBackend = 'direct' | 'comfyui';

export interface TextRequest {
  platform: Platform;
  content_type: string;
  topic: string;
  context?: string;
  tone?: string;
  model?: string;
}

export interface T2IRequest {
  prompt: string;
  width: number;
  height: number;
  seed?: number;
  backend: ImageBackend;
}

export interface ImageResult {
  job_id: string;
  status: string;
  filename?: string;
  error?: string;
}

export interface AuthStatus {
  youtube: boolean;
  instagram: boolean;
  linkedin: boolean;
}

export interface DimensionPreset {
  label: string;
  width: number;
  height: number;
}

export const PLATFORM_DIMENSIONS: Record<Platform, DimensionPreset[]> = {
  youtube: [
    { label: 'Thumbnail', width: 1280, height: 720 },
    { label: 'Banner', width: 2560, height: 1440 },
  ],
  instagram: [
    { label: 'Square Post', width: 1080, height: 1080 },
    { label: 'Portrait', width: 1080, height: 1350 },
    { label: 'Story/Reel', width: 1080, height: 1920 },
  ],
  linkedin: [
    { label: 'Link Post', width: 1200, height: 627 },
    { label: 'Banner', width: 1584, height: 396 },
    { label: 'Square', width: 1080, height: 1080 },
  ],
};

export const PLATFORM_TEXT_TYPES: Record<Platform, { value: string; label: string }[]> = {
  youtube: [
    { value: 'title', label: 'Video Title' },
    { value: 'description', label: 'Description' },
    { value: 'tags', label: 'Tags' },
    { value: 'script', label: 'Script' },
    { value: 'thumbnail_prompt', label: 'Thumbnail Prompt' },
  ],
  instagram: [
    { value: 'caption', label: 'Caption' },
    { value: 'hashtags', label: 'Hashtags' },
    { value: 'carousel', label: 'Carousel Plan' },
    { value: 'reel_script', label: 'Reel Script' },
  ],
  linkedin: [
    { value: 'post', label: 'Post' },
    { value: 'article', label: 'Article' },
    { value: 'banner_prompt', label: 'Banner Prompt' },
  ],
};

export const TEXT_MODELS = [
  { value: 'gpt-5-mini', label: 'GPT-5 Mini (Fast)' },
  { value: 'gpt-4o', label: 'GPT-4o' },
  { value: 'gpt-4.1', label: 'GPT-4.1 (Best)' },
];
