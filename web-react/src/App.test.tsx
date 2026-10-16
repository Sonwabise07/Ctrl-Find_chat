import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { fixtures } from './test/fixtures';
import { mockApi } from './test/mockApi';

beforeEach(() => {
  window.location.hash = '';
  mockApi({
    'GET /api/assistant/meta': fixtures.meta,
    'GET /api/dashboards/overview': fixtures.overview,
    'GET /api/dashboards/operational': fixtures.operational,
    'GET /api/dashboards/management': fixtures.management,
    'POST /api/assistant/ask': fixtures.opened,
  });
});

describe('App', () => {
  it('opens on the dashboard and shows who is signed in', async () => {
    render(<App />);
    expect(await screen.findByText('Total registered assets')).toBeInTheDocument();
    expect(await screen.findByText(/Fixed Assets team/)).toBeInTheDocument();
  });

  it('moves between the pages from the menu, and switches report tabs', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole('link', { name: 'Reports' }));
    expect(await screen.findByText('Purchases by month')).toBeInTheDocument();

    await user.click(screen.getByRole('tab', { name: 'Management' }));
    expect(await screen.findByText('Financial exposure')).toBeInTheDocument();
  });

  it('lists what the assistant supports on its own page, with no floating bubble there', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(screen.getByRole('link', { name: 'Data assistant' }));
    expect(await screen.findByText('Supported question types')).toBeInTheDocument();
    for (const category of fixtures.meta.categories) {
      expect(screen.getByText(category.label)).toBeInTheDocument();
    }
    expect(
      screen.queryByRole('button', { name: 'Open the data assistant' }),
    ).not.toBeInTheDocument();
  });

  it('opens the floating assistant on other pages, and a dashboard it shows opens as a page', async () => {
    const user = userEvent.setup();
    render(<App />);
    await user.click(await screen.findByRole('button', { name: 'Open the data assistant' }));

    await user.type(screen.getByLabelText('Your question'), 'Open the Operational dashboard');
    await user.click(screen.getByRole('button', { name: 'Send question' }));
    await user.click(await screen.findByRole('button', { name: 'Open full page' }));

    expect(window.location.hash).toBe('#/reports/operational');
    expect(
      await screen.findByRole('tab', { name: 'Operational', selected: true }),
    ).toBeInTheDocument();
  });
});
