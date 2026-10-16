import type { ReactNode } from 'react';
import './widgets.css';

export function WidgetCard({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="widget-card">
      <h3 className="widget-card__title">{title}</h3>
      {children}
    </section>
  );
}
