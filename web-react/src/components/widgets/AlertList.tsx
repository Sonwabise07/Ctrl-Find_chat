import type { AlertsData } from '../../api/types';
import './widgets.css';

export function AlertList({ rows }: AlertsData) {
  if (rows.length === 0) return <p className="widget-note">Nothing needs attention.</p>;
  return (
    <ul className="alert-list">
      {rows.map((row, index) => (
        <li key={index} className="alert-list__item">
          <span className={`alert-list__dot tone-${row.tone}`} aria-hidden="true" />
          <div>
            <p className="alert-list__title">{row.title}</p>
            <p className="alert-list__subtitle">{row.subtitle}</p>
          </div>
        </li>
      ))}
    </ul>
  );
}
