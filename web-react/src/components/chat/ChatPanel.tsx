import { useEffect, useId, useRef, useState, type FormEvent } from 'react';
import type { Chip } from '../../api/types';
import { Icon } from '../Icon';
import { MessageRow } from './MessageRow';
import { Suggestions } from './Suggestions';
import { useChat } from './useChat';
import './chat.css';

interface Props {
  /** `page` fills the Data assistant page. `sheet` is the floating panel opened from any page. */
  variant: 'page' | 'sheet';
  /** Questions offered before anything has been asked. */
  suggestions: Chip[];
  onClose?: () => void;
  onOpenDashboard?: (id: string) => void;
}

const WELCOME =
  "Ask me about assets, warranties, repairs and audits. I only answer from this system's own data.";

export function ChatPanel({ variant, suggestions, onClose, onOpenDashboard }: Props) {
  const { messages, busy, ask } = useChat();
  const [draft, setDraft] = useState('');
  const log = useRef<HTMLDivElement>(null);
  const inputId = useId();

  useEffect(() => {
    if (log.current) log.current.scrollTop = log.current.scrollHeight;
  }, [messages]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void ask(draft);
    setDraft('');
  };

  return (
    <section className={`chat chat--${variant}`} aria-label="Data assistant chat">
      {variant === 'page' ? (
        <header className="chat__header">
          <h2>Ask about your assets</h2>
          <p>Answers only from this system&apos;s own data · never Atom directly</p>
        </header>
      ) : (
        <header className="chat__header chat__header--sheet">
          <span className="chat__logo">
            <Icon name="spark" />
          </span>
          <div>
            <h2>Data assistant</h2>
            <p>Answers from this system&apos;s data only</p>
          </div>
          <button
            type="button"
            className="chat__close"
            onClick={onClose}
            aria-label="Close the assistant"
          >
            <Icon name="close" />
          </button>
        </header>
      )}

      <div className="chat__log" ref={log} role="log" aria-live="polite">
        {messages.length === 0 && (
          <>
            <div className="bubble bubble--assistant">{WELCOME}</div>
            <Suggestions chips={suggestions} onAsk={ask} />
          </>
        )}
        {messages.map((message) => (
          <MessageRow
            key={message.id}
            message={message}
            onAsk={ask}
            onOpenDashboard={onOpenDashboard}
          />
        ))}
      </div>

      <form className="chat__form" onSubmit={submit}>
        <label htmlFor={inputId} className="visually-hidden">
          Your question
        </label>
        <input
          id={inputId}
          className="chat__input"
          value={draft}
          maxLength={300}
          autoComplete="off"
          placeholder="Ask a question about assets, warranty, audits or losses…"
          onChange={(event) => setDraft(event.target.value)}
        />
        <button
          className="chat__send"
          type="submit"
          disabled={busy || !draft.trim()}
          aria-label="Send question"
        >
          <Icon name="send" />
        </button>
      </form>
    </section>
  );
}
