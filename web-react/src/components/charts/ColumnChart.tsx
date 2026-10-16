import type { ChartRow } from '../../api/types';
import './charts.css';

const WIDTH = 520;
const HEIGHT = 200;
/** Above this many columns, every other month is labelled so the labels stay readable. */
const MAX_ALL_LABELS = 8;
const PAD = { top: 26, bottom: 30, side: 12 };

interface Props {
  rows: ChartRow[];
  label: string;
}

/** Vertical columns for change over time. Only the highest column is labelled; hover shows the rest. */
export function ColumnChart({ rows, label }: Props) {
  const largest = Math.max(0, ...rows.map((row) => row.value));
  const slot = (WIDTH - PAD.side * 2) / Math.max(rows.length, 1);
  const barWidth = Math.min(slot * 0.6, 44);
  const plotHeight = HEIGHT - PAD.top - PAD.bottom;
  const baseline = HEIGHT - PAD.bottom;
  const showLabel = (index: number) =>
    rows.length <= MAX_ALL_LABELS || (rows.length - 1 - index) % 2 === 0; // the latest month is always labelled
  const peak = largest > 0 ? rows.findIndex((row) => row.value === largest) : -1;

  return (
    <svg className="column-chart" viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={label}>
      <line
        className="column-chart__axis"
        x1={PAD.side}
        x2={WIDTH - PAD.side}
        y1={baseline}
        y2={baseline}
      />
      {rows.map((row, index) => {
        const height = largest ? (row.value / largest) * plotHeight : 0;
        const x = PAD.side + slot * index + (slot - barWidth) / 2;
        const y = baseline - Math.max(height, row.value > 0 ? 2 : 0);
        const centre = x + barWidth / 2;
        return (
          <g key={row.label}>
            <rect
              className="column-chart__bar"
              x={x}
              y={y}
              width={barWidth}
              height={baseline - y}
              rx={3}
            >
              <title>{`${row.label}: ${row.text}`}</title>
            </rect>
            {showLabel(index) && (
              <text className="column-chart__label" x={centre} y={HEIGHT - 10} textAnchor="middle">
                {row.label}
              </text>
            )}
            {index === peak && (
              <text className="column-chart__value" x={centre} y={y - 6} textAnchor="middle">
                {row.text}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}
