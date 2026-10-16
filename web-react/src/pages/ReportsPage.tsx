import { PageHeader } from '../shell/PageHeader';
import type { ReportsTab } from '../shell/routes';
import { DashboardBody } from './DashboardBody';

const TABS: { id: ReportsTab; label: string }[] = [
  { id: 'operational', label: 'Operational' },
  { id: 'management', label: 'Management' },
];

interface Props {
  tab: ReportsTab;
  onTab: (tab: ReportsTab) => void;
}

export function ReportsPage({ tab, onTab }: Props) {
  return (
    <>
      <PageHeader title="Reports" subtitle="Operational and management dashboards" />
      <div className="tabs" role="tablist">
        {TABS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={item.id === tab}
            className={item.id === tab ? 'tabs__tab tabs__tab--current' : 'tabs__tab'}
            onClick={() => onTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>
      <DashboardBody id={tab} />
    </>
  );
}
