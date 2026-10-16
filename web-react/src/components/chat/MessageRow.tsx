import { AssistantMessage } from './AssistantMessage';
import type { Message } from './useChat';

interface Props {
  message: Message;
  onAsk: (question: string) => void;
  onOpenDashboard?: (id: string) => void;
}

export function MessageRow({ message, onAsk, onOpenDashboard }: Props) {
  if (message.role === 'user') return <div className="bubble bubble--user">{message.text}</div>;
  if (message.state === 'pending') {
    return (
      <div className="bubble bubble--assistant" role="status" aria-label="Looking that up">
        <span className="dots" aria-hidden="true">
          <i />
          <i />
          <i />
        </span>
      </div>
    );
  }
  if (message.state === 'error') {
    return (
      <div className="bubble bubble--assistant bubble--error">
        Something went wrong on our side. Try again.
      </div>
    );
  }
  return <AssistantMessage reply={message.reply} onAsk={onAsk} onOpenDashboard={onOpenDashboard} />;
}
