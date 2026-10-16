import { useCallback, useEffect, useState } from 'react';

export type ReportsTab = 'operational' | 'management';
export type Route =
  { page: 'dashboard' } | { page: 'reports'; tab: ReportsTab } | { page: 'assistant' };

/** Routes live in the URL hash so the prototype needs no router. The main system uses its own. */
export function parseRoute(hash: string): Route {
  const [page, tab] = hash.replace(/^#\/?/, '').split('/');
  if (page === 'reports') return { page, tab: tab === 'management' ? 'management' : 'operational' };
  if (page === 'assistant') return { page };
  return { page: 'dashboard' };
}

export const routeHash = (route: Route) =>
  route.page === 'reports' ? `#/reports/${route.tab}` : `#/${route.page}`;

/** Where an opened dashboard lives as a full page. */
export const routeForDashboard = (id: string): Route =>
  id === 'operational' || id === 'management'
    ? { page: 'reports', tab: id }
    : { page: 'dashboard' };

export function useRoute(): [Route, (route: Route) => void] {
  const [route, setRoute] = useState(() => parseRoute(window.location.hash));
  useEffect(() => {
    const sync = () => setRoute(parseRoute(window.location.hash));
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);
  const navigate = useCallback((next: Route) => {
    window.location.hash = routeHash(next);
  }, []);
  return [route, navigate];
}
