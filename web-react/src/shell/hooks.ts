import { useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Dashboard, Meta } from '../api/types';

/** Suggested questions, the supported-types list and who is signed in. Null until it has loaded. */
export function useMeta(): Meta | null {
  const [meta, setMeta] = useState<Meta | null>(null);
  useEffect(() => {
    let active = true;
    api
      .meta()
      .then((loaded) => active && setMeta(loaded))
      .catch(() => undefined);
    return () => {
      active = false;
    };
  }, []);
  return meta;
}

export type DashboardState =
  { status: 'loading' } | { status: 'error' } | { status: 'ready'; dashboard: Dashboard };

export function useDashboard(id: string): DashboardState {
  const [state, setState] = useState<DashboardState>({ status: 'loading' });
  useEffect(() => {
    let active = true;
    setState({ status: 'loading' });
    api
      .dashboard(id)
      .then((dashboard) => active && setState({ status: 'ready', dashboard }))
      .catch(() => active && setState({ status: 'error' }));
    return () => {
      active = false;
    };
  }, [id]);
  return state;
}
