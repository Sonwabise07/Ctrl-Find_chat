import type { TrendsData } from '../../api/types';
import './widgets.css';

const ARROWS = { up: '↑', down: '↓', flat: '→' } as const;

export function TrendTable({ rows }: TrendsData) {
  return (
    <div className="table-wrap">
      <table className="data-table" aria-label="This month against last month">
        <thead>
          <tr>
            <th scope="col">Topic</th>
            <th scope="col">This month</th>
            <th scope="col">Last month</th>
            <th scope="col">Trend</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td>{row.label}</td>
              <td>{row.text}</td>
              <td>{row.previous_text}</td>
              <td className={`trend tone-${row.tone}`}>
                {ARROWS[row.direction]} {row.change}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
