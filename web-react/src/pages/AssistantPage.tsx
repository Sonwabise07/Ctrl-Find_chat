import type { Meta } from '../api/types';
import { ChatPanel } from '../components/chat/ChatPanel';
import { SupportedTypes } from '../components/chat/SupportedTypes';
import { PageHeader } from '../shell/PageHeader';

interface Props {
  meta: Meta | null;
  onOpenDashboard: (id: string) => void;
}

export function AssistantPage({ meta, onOpenDashboard }: Props) {
  return (
    <>
      <PageHeader
        title="Data assistant"
        subtitle="Plain-English questions, answered only from this system's own data"
      />
      <div className="assistant-page">
        <ChatPanel
          variant="page"
          suggestions={meta?.chips.slice(0, 3) ?? []}
          onOpenDashboard={onOpenDashboard}
        />
        <SupportedTypes categories={meta?.categories ?? []} />
      </div>
    </>
  );
}
