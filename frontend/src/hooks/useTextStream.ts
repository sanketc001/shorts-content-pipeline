import { useState, useCallback, useRef } from 'react';
import { generateTextStream } from '../api/client';
import type { TextRequest } from '../types';

export function useTextStream() {
  const [output, setOutput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef(false);

  const generate = useCallback(async (req: TextRequest) => {
    setOutput('');
    setError(null);
    setIsGenerating(true);
    abortRef.current = false;

    await generateTextStream(
      req,
      (chunk) => {
        if (!abortRef.current) {
          setOutput((prev) => prev + chunk);
        }
      },
      () => setIsGenerating(false),
      (err) => {
        setError(err);
        setIsGenerating(false);
      },
    );
  }, []);

  const stop = useCallback(() => {
    abortRef.current = true;
    setIsGenerating(false);
  }, []);

  const clear = useCallback(() => {
    setOutput('');
    setError(null);
  }, []);

  return { output, isGenerating, error, generate, stop, clear };
}
