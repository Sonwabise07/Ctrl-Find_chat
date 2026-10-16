import type { Widget } from '../../api/types';
import { BarList } from '../charts/BarList';
import { ColumnChart } from '../charts/ColumnChart';
import { DataTable } from '../DataTable';
import { AlertList } from './AlertList';
import { KeyValueList } from './KeyValueList';
import { KpiCard } from './KpiCard';
import { TrendTable } from './TrendTable';
import { WidgetCard } from './WidgetCard';

/** Draws one dashboard widget from the API. The widget's `type` decides how. */
export function WidgetRenderer({ widget }: { widget: Widget }) {
  const unavailable = (
    <WidgetCard title={widget.title}>
      <p className="widget-note">Needs data that is not in the system yet.</p>
    </WidgetCard>
  );

  switch (widget.type) {
    case 'kpi':
      return widget.data ? (
        <KpiCard title={widget.title} tone={widget.tone} data={widget.data} />
      ) : (
        unavailable
      );
    case 'bars':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <BarList rows={widget.data.rows} label={widget.title} showShare />
        </WidgetCard>
      ) : (
        unavailable
      );
    case 'columns':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <ColumnChart rows={widget.data.rows} label={widget.title} />
        </WidgetCard>
      ) : (
        unavailable
      );
    case 'table':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <DataTable columns={widget.data.columns} rows={widget.data.rows} label={widget.title} />
        </WidgetCard>
      ) : (
        unavailable
      );
    case 'list':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <AlertList rows={widget.data.rows} />
        </WidgetCard>
      ) : (
        unavailable
      );
    case 'trends':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <TrendTable rows={widget.data.rows} />
        </WidgetCard>
      ) : (
        unavailable
      );
    case 'keyvalue':
      return widget.data ? (
        <WidgetCard title={widget.title}>
          <KeyValueList rows={widget.data.rows} />
        </WidgetCard>
      ) : (
        unavailable
      );
  }
}
