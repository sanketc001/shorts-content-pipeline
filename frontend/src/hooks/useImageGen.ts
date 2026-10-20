import { useState, useCallback } from 'react';
import { generateT2I, generateI2I, getImageUrl } from '../api/client';
import type { ImageBackend } from '../types';

export function useImageGen() {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateT2i = useCallback(
    async (prompt: string, width: number, height: number, backend: ImageBackend) => {
      setError(null);
      setIsGenerating(true);
      setImageUrl(null);

      try {
        const result = await generateT2I({ prompt, width, height, backend });
        if (result.filename) {
          setImageUrl(getImageUrl(result.filename));
        }
      } catch (e: any) {
        setError(e.message || 'Image generation failed');
      } finally {
        setIsGenerating(false);
      }
    },
    [],
  );

  const generateI2i = useCallback(
    async (
      prompt: string,
      imageFile: File,
      denoise: number,
      backend: ImageBackend,
    ) => {
      setError(null);
      setIsGenerating(true);
      setImageUrl(null);

      try {
        const formData = new FormData();
        formData.append('prompt', prompt);
        formData.append('denoise', denoise.toString());
        formData.append('backend', backend);
        formData.append('image', imageFile);

        const result = await generateI2I(formData);
        if (result.filename) {
          setImageUrl(getImageUrl(result.filename));
        }
      } catch (e: any) {
        setError(e.message || 'Image generation failed');
      } finally {
        setIsGenerating(false);
      }
    },
    [],
  );

  const clear = useCallback(() => {
    setImageUrl(null);
    setError(null);
  }, []);

  return { imageUrl, isGenerating, error, generateT2i, generateI2i, clear };
}
