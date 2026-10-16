import { useState } from 'react';
import type { Chip } from '../api/types';
import { ChatPanel } from '../components/chat/ChatPanel';
import { Icon } from '../components/Icon';

interface Props {
  suggestions: Chip[];
  onOpenDashboard: (id: string) => void;
}

/** The chat bubble in the corner of every page except the Data assistant page. */
export function FloatingChat({ suggestions, onOpenDashboard }: Props) {
  const [open, setOpen] = useState(false);
  return (
    <>
      {/* Kept mounted while closed so the conversation is still there when it is reopened. */}
      <div className="floating-chat__sheet" hidden={!open}>
        <ChatPanel
          variant="sheet"
          suggestions={suggestions}
          onClose={() => setOpen(false)}
          onOpenDashboard={(id) => {
            setOpen(false);
            onOpenDashboard(id);
          }}
        />
      </div>
      {!open && (
        <button
          type="button"
          className="floating-chat__button"
          onClick={() => setOpen(true)}
          aria-label="Open the data assistant"
        >
          <Icon name="chat" />
        </button>
      )}
    </>
  );
}
