import type { Chart } from '../../api/types';
import { BarList } from './BarList';
import { ColumnChart } from './ColumnChart';

/** A chart from a chat reply: columns for change over time, bars for comparing groups. */
export function ChartView({ chart }: { chart: Chart }) {
  return (
    <figure className="chart-view">
      {chart.kind === 'columns' ? (
        <ColumnChart rows={chart.rows} label={chart.note} />
      ) : (
        <BarList rows={chart.rows} label={chart.note} />
      )}
      <figcaption className="chart-view__note">{chart.note}</figcaption>
    </figure>
  );
}
