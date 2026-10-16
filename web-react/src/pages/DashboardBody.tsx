import { DashboardView } from '../components/dashboard/DashboardView';
import { useDashboard } from '../shell/hooks';

/** Loads a dashboard by id and shows it, with a plain message while loading or if it fails. */
export function DashboardBody({ id }: { id: string }) {
  const state = useDashboard(id);
  if (state.status === 'loading') return <p className="page-note">Loading…</p>;
  if (state.status === 'error')
    return <p className="page-note page-note--error">The dashboard could not be loaded.</p>;
  return <DashboardView dashboard={state.dashboard} />;
}
