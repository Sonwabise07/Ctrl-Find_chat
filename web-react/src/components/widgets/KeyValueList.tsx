import type { KeyValueData } from '../../api/types';
import './widgets.css';

export function KeyValueList({ rows }: KeyValueData) {
  return (
    <dl className="key-values">
      {rows.map((row) => (
        <div key={row.label} className="key-values__row">
          <dt>{row.label}</dt>
          <dd>{row.text}</dd>
        </div>
      ))}
    </dl>
  );
}
