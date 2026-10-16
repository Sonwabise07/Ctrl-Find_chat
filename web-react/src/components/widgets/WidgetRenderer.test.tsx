import { render, screen } from '@testing-library/react';
import type { Widget } from '../../api/types';
import { fixtures } from '../../test/fixtures';
import { WidgetRenderer } from './WidgetRenderer';

const everyWidget = [fixtures.overview, fixtures.operational, fixtures.management].flatMap(
  (d) => d.widgets,
);

describe('WidgetRenderer', () => {
  it.each(everyWidget.map((widget) => [widget.id, widget] as const))(
    'draws the %s widget',
    (_id, widget) => {
      render(<WidgetRenderer widget={widget} />);
      expect(screen.getByText(widget.title)).toBeInTheDocument();
    },
  );

  it('covers every widget type the API can send', () => {
    const types = new Set(everyWidget.map((widget) => widget.type));
    expect(types).toEqual(
      new Set(['kpi', 'bars', 'columns', 'table', 'list', 'trends', 'keyvalue']),
    );
  });

  it('shows a KPI card with its figure and tag', () => {
    const kpi = fixtures.overview.widgets.find((widget) => widget.type === 'kpi')!;
    render(<WidgetRenderer widget={kpi} />);
    if (kpi.type !== 'kpi' || !kpi.data) throw new Error('fixture is not a kpi');
    expect(screen.getByText(kpi.data.text)).toBeInTheDocument();
    expect(screen.getByText(kpi.data.tag!)).toBeInTheDocument();
  });

  it('shows the trend direction and change for each topic', () => {
    const trends = fixtures.operational.widgets.find((widget) => widget.type === 'trends')!;
    render(<WidgetRenderer widget={trends} />);
    if (trends.type !== 'trends' || !trends.data) throw new Error('fixture is not trends');
    expect(screen.getAllByRole('row')).toHaveLength(trends.data.rows.length + 1);
    expect(
      document.querySelector('.trend.tone-good, .trend.tone-bad, .trend.tone-neutral'),
    ).toBeInTheDocument();
  });

  it('says so when a widget needs data the system does not have yet', () => {
    const missing = { ...fixtures.management.widgets[2], available: false, data: null } as Widget;
    render(<WidgetRenderer widget={missing} />);
    expect(screen.getByText('Needs data that is not in the system yet.')).toBeInTheDocument();
  });
});
