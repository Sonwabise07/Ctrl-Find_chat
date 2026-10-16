import { AssistantPage } from './pages/AssistantPage';
import { DashboardPage } from './pages/DashboardPage';
import { ReportsPage } from './pages/ReportsPage';
import { FloatingChat } from './shell/FloatingChat';
import { useMeta } from './shell/hooks';
import { routeForDashboard, useRoute } from './shell/routes';
import { Sidebar } from './shell/Sidebar';
import './shell/shell.css';

export default function App() {
  const [route, navigate] = useRoute();
  const meta = useMeta();
  const openDashboard = (id: string) => navigate(routeForDashboard(id));

  return (
    <div className="shell">
      <Sidebar route={route} navigate={navigate} user={meta?.user} />
      <main className="shell__main">
        {route.page === 'dashboard' && <DashboardPage />}
        {route.page === 'reports' && (
          <ReportsPage tab={route.tab} onTab={(tab) => navigate({ page: 'reports', tab })} />
        )}
        {route.page === 'assistant' && (
          <AssistantPage meta={meta} onOpenDashboard={openDashboard} />
        )}
      </main>
      {route.page !== 'assistant' && (
        <FloatingChat suggestions={meta?.chips.slice(0, 3) ?? []} onOpenDashboard={openDashboard} />
      )}
    </div>
  );
}
