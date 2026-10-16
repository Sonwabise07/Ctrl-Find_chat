import { useCallback, useRef, useState } from 'react';
import { api } from '../../api/client';
import type { Context, Reply } from '../../api/types';

export type Message =
  | { id: number; role: 'user'; text: string }
  | { id: number; role: 'assistant'; state: 'pending' }
  | { id: number; role: 'assistant'; state: 'error' }
  | { id: number; role: 'assistant'; state: 'reply'; reply: Reply };

/** The conversation: what was said, and what the next question needs to know about the last answer. */
export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);
  const context = useRef<Context | null>(null);
  const working = useRef(false);
  const nextId = useRef(1);

  const ask = useCallback(async (question: string) => {
    const text = question.trim();
    if (!text || working.current) return;
    working.current = true;
    setBusy(true);

    const userId = nextId.current++;
    const answerId = nextId.current++;
    const settle = (message: Message) =>
      setMessages((all) => all.map((m) => (m.id === answerId ? message : m)));
    setMessages((all) => [
      ...all,
      { id: userId, role: 'user', text },
      { id: answerId, role: 'assistant', state: 'pending' },
    ]);

    try {
      const reply = await api.ask({ question: text, context: context.current });
      if (reply.scope === 'in') context.current = { intent: reply.intent, slots: reply.slots };
      settle({ id: answerId, role: 'assistant', state: 'reply', reply });
    } catch {
      settle({ id: answerId, role: 'assistant', state: 'error' });
    } finally {
      working.current = false;
      setBusy(false);
    }
  }, []);

  return { messages, busy, ask };
}
