import type { ChartRow } from '../../api/types';
import './charts.css';

interface Props {
  rows: ChartRow[];
  label: string;
  showShare?: boolean;
}

/** Horizontal bars for comparing groups. One colour: position and length carry the meaning. */
export function BarList({ rows, label, showShare = false }: Props) {
  const largest = Math.max(0, ...rows.map((row) => row.value));
  return (
    <ul className="bar-list" aria-label={label}>
      {rows.map((row) => (
        <li key={row.label} className="bar-list__row">
          <span className="bar-list__label">{row.label}</span>
          <span className="bar-list__track">
            <span className="bar-list__fill" style={{ width: `${widthOf(row.value, largest)}%` }} />
          </span>
          <span className="bar-list__value">
            {row.text}
            {showShare && row.share !== undefined && (
              <span className="bar-list__share"> {Math.round(row.share)}%</span>
            )}
          </span>
        </li>
      ))}
    </ul>
  );
}

/** A tiny value still gets a visible sliver. */
const widthOf = (value: number, largest: number) =>
  largest === 0 ? 0 : Math.max((value / largest) * 100, value > 0 ? 2 : 0);
