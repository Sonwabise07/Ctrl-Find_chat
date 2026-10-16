import { vi } from 'vitest';

type Handler = unknown | ((body: unknown) => unknown);

export interface Call {
  method: string;
  path: string;
  body: any;
}

/** Replaces `fetch` with canned replies, keyed like `POST /api/assistant/ask`. Returns the calls made. */
export function mockApi(routes: Record<string, Handler>): Call[] {
  const calls: Call[] = [];
  vi.stubGlobal(
    'fetch',
    vi.fn(async (input: string, init?: RequestInit) => {
      const url = new URL(input, 'http://localhost');
      const method = init?.method ?? 'GET';
      const body = init?.body ? JSON.parse(String(init.body)) : undefined;
      calls.push({ method, path: url.pathname, body });

      const handler = routes[`${method} ${url.pathname}`];
      if (handler === undefined) return json({ error: 'not found' }, 404);
      const result = typeof handler === 'function' ? handler(body) : handler;
      return result instanceof Response ? result : json(result, 200);
    }),
  );
  return calls;
}

const json = (body: unknown, status: number) =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

export const serverError = () => json({ error: 'boom' }, 500);
