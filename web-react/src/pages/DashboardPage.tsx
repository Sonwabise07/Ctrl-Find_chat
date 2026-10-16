import { PageHeader } from '../shell/PageHeader';
import { DashboardBody } from './DashboardBody';

export function DashboardPage() {
  return (
    <>
      <PageHeader title="Dashboard" subtitle="Fixed Assets · overview" />
      <DashboardBody id="overview" />
    </>
  );
}
