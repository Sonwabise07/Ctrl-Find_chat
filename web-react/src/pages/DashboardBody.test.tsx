import { render, screen } from '@testing-library/react';
import { fixtures } from '../test/fixtures';
import { mockApi, serverError } from '../test/mockApi';
import { DashboardBody } from './DashboardBody';

describe('DashboardBody', () => {
  it('shows a loading note, then every widget', async () => {
    mockApi({ 'GET /api/dashboards/overview': fixtures.overview });
    render(<DashboardBody id="overview" />);
    expect(screen.getByText('Loading…')).toBeInTheDocument();
    for (const widget of fixtures.overview.widgets) {
      expect(await screen.findByText(widget.title)).toBeInTheDocument();
    }
  });

  it('says so when the dashboard cannot be loaded', async () => {
    mockApi({ 'GET /api/dashboards/overview': serverError });
    render(<DashboardBody id="overview" />);
    expect(await screen.findByText('The dashboard could not be loaded.')).toBeInTheDocument();
  });
});
