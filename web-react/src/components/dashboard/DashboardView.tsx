import type { Dashboard } from '../../api/types';
import { WidgetRenderer } from '../widgets/WidgetRenderer';
import './dashboard.css';

interface Props {
  dashboard: Dashboard;
  /** One column, for showing a dashboard inside a chat reply. */
  compact?: boolean;
}

export function DashboardView({ dashboard, compact = false }: Props) {
  return (
    <div className={compact ? 'dashboard-grid dashboard-grid--compact' : 'dashboard-grid'}>
      {dashboard.widgets.map((widget) => (
        <div
          key={widget.id}
          className={`dashboard-grid__item dashboard-grid__item--${widget.size}`}
        >
          <WidgetRenderer widget={widget} />
        </div>
      ))}
    </div>
  );
}
