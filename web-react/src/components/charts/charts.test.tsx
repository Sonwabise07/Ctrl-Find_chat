import { render, screen } from '@testing-library/react';
import { fixtures } from '../../test/fixtures';
import { BarList } from './BarList';
import { ChartView } from './ChartView';
import { ColumnChart } from './ColumnChart';

const rows = [
  { label: 'Assigned', value: 26, text: '26', share: 61.9 },
  { label: 'Available', value: 9, text: '9', share: 21.4 },
  { label: 'Lost', value: 0, text: '0', share: 0 },
];

describe('BarList', () => {
  it('draws the longest bar at full width and the others in proportion', () => {
    const { container } = render(<BarList rows={rows} label="By status" />);
    const widths = [...container.querySelectorAll<HTMLElement>('.bar-list__fill')].map(
      (bar) => bar.style.width,
    );
    expect(widths[0]).toBe('100%');
    expect(parseFloat(widths[1])).toBeCloseTo((9 / 26) * 100);
    expect(widths[2]).toBe('0%');
  });

  it('shows each share only when asked', () => {
    const { rerender } = render(<BarList rows={rows} label="By status" />);
    expect(screen.queryByText('62%')).not.toBeInTheDocument();
    rerender(<BarList rows={rows} label="By status" showShare />);
    expect(screen.getByText('62%')).toBeInTheDocument();
  });

  it('copes with no data', () => {
    render(<BarList rows={[]} label="Empty" />);
    expect(screen.getByRole('list', { name: 'Empty' })).toBeEmptyDOMElement();
  });
});

describe('ColumnChart', () => {
  const months = fixtures.trend.chart!.rows;

  it('draws one column per month with a hover title on each', () => {
    const { container } = render(<ColumnChart rows={months} label="Purchases" />);
    expect(container.querySelectorAll('rect.column-chart__bar')).toHaveLength(months.length);
    expect(container.querySelectorAll('rect.column-chart__bar title')).toHaveLength(months.length);
  });

  it('labels only the highest month', () => {
    const { container } = render(<ColumnChart rows={months} label="Purchases" />);
    const peak = months.reduce((best, row) => (row.value > best.value ? row : best));
    const labelled = container.querySelectorAll('text.column-chart__value');
    expect(labelled).toHaveLength(1);
    expect(labelled[0].textContent).toBe(peak.text);
  });

  it('draws a flat chart with no value label when everything is zero', () => {
    const flat = months.map((row) => ({ ...row, value: 0, text: 'R0' }));
    const { container } = render(<ColumnChart rows={flat} label="Nothing" />);
    expect(container.querySelectorAll('text.column-chart__value')).toHaveLength(0);
    expect(container.querySelectorAll('rect.column-chart__bar')).toHaveLength(flat.length);
  });
});

describe('ChartView', () => {
  it('uses columns for change over time and bars for groups', () => {
    const { container, rerender } = render(<ChartView chart={fixtures.trend.chart!} />);
    expect(container.querySelector('svg.column-chart')).toBeInTheDocument();
    rerender(<ChartView chart={fixtures.split.chart!} />);
    expect(container.querySelector('ul.bar-list')).toBeInTheDocument();
    expect(screen.getByText(fixtures.split.chart!.note)).toBeInTheDocument();
  });
});

describe('ColumnChart labels', () => {
  const months = fixtures.trend.chart!.rows;

  it('labels every other month when there are many, and always the latest', () => {
    const { container } = render(<ColumnChart rows={months} label="Purchases" />);
    const labels = [...container.querySelectorAll('text.column-chart__label')].map(
      (node) => node.textContent,
    );
    expect(labels).toHaveLength(months.length / 2);
    expect(labels.at(-1)).toBe(months.at(-1)!.label);
  });

  it('labels every month when there are few', () => {
    const { container } = render(<ColumnChart rows={months.slice(0, 6)} label="Six months" />);
    expect(container.querySelectorAll('text.column-chart__label')).toHaveLength(6);
  });
});
