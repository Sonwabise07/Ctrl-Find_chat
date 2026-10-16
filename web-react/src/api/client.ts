import type { AskRequest, Dashboard, DashboardSummary, Meta, Reply } from './types';

const BASE = '/api';

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

/**
 * Demo only: the prototype backend picks the user from `?as=<email>`.
 * The main system takes the user from the login instead, so delete this and send the token.
 */
const demoUser = () => new URLSearchParams(window.location.search).get('as') ?? undefined;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(BASE + path, init);
  if (!response.ok) {
    const body = await response.json().catch(() => ({ error: response.statusText }));
    throw new ApiError(response.status, body.error ?? response.statusText);
  }
  return response.json() as Promise<T>;
}

const withUser = (path: string) => {
  const email = demoUser();
  return email ? `${path}?as=${encodeURIComponent(email)}` : path;
};

export const api = {
  meta: () => request<Meta>(withUser('/assistant/meta')),
  ask: (body: AskRequest) =>
    request<Reply>('/assistant/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...body, as: demoUser() }),
    }),
  dashboards: () => request<DashboardSummary[]>('/dashboards'),
  dashboard: (id: string) => request<Dashboard>(withUser(`/dashboards/${id}`)),
};
