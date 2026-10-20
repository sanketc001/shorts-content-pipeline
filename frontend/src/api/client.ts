import type { TextRequest, T2IRequest, ImageResult, AuthStatus } from '../types';

export async function generateTextStream(
  req: TextRequest,
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
): Promise<void> {
  const resp = await fetch('/api/text/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });

  if (!resp.ok) {
    onError(`HTTP ${resp.status}: ${resp.statusText}`);
    return;
  }

  const reader = resp.body?.getReader();
  if (!reader) {
    onError('No response body');
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (data === '[DONE]') {
          onDone();
          return;
        }
        onChunk(data);
      } else if (line.startsWith('event: error')) {
        // Next data line is the error
      }
    }
  }
  onDone();
}

export async function generateT2I(req: T2IRequest): Promise<ImageResult> {
  const resp = await fetch('/api/image/t2i', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

export async function generateI2I(formData: FormData): Promise<ImageResult> {
  const resp = await fetch('/api/image/i2i', {
    method: 'POST',
    body: formData,
  });
  if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
  return resp.json();
}

export async function getImageBackends(): Promise<Record<string, { available: boolean; description: string }>> {
  const resp = await fetch('/api/image/backends');
  return resp.json();
}

export async function getAuthStatus(): Promise<AuthStatus> {
  const resp = await fetch('/api/auth/status');
  return resp.json();
}

export function getImageUrl(filename: string): string {
  return `/api/image/result/${filename}`;
}
