import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { fixtures } from '../../test/fixtures';
import { mockApi, serverError } from '../../test/mockApi';
import { ChatPanel } from './ChatPanel';

const ASK = 'POST /api/assistant/ask';

async function ask(question: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Your question'), question);
  await user.click(screen.getByRole('button', { name: 'Send question' }));
}

const renderPanel = (props: Partial<Parameters<typeof ChatPanel>[0]> = {}) =>
  render(<ChatPanel variant="page" suggestions={fixtures.meta.chips.slice(0, 3)} {...props} />);

describe('ChatPanel', () => {
  it('greets the user and offers suggested questions', () => {
    renderPanel();
    expect(screen.getByText(/I only answer from this system's own data/)).toBeInTheDocument();
    for (const chip of fixtures.meta.chips.slice(0, 3)) {
      expect(screen.getByRole('button', { name: chip.label })).toBeInTheDocument();
    }
  });

  it('shows the question, then the answer with its source line', async () => {
    mockApi({ [ASK]: fixtures.count });
    renderPanel();
    await ask('How many laptops are available?');
    expect(screen.getByText('How many laptops are available?')).toBeInTheDocument();
    expect(await screen.findByText('3 laptops')).toBeInTheDocument();
    expect(screen.getByText(fixtures.count.source!)).toBeInTheDocument();
  });

  it('keeps the send button off until there is a question', async () => {
    renderPanel();
    expect(screen.getByRole('button', { name: 'Send question' })).toBeDisabled();
    await userEvent.setup().type(screen.getByLabelText('Your question'), 'hi');
    expect(screen.getByRole('button', { name: 'Send question' })).toBeEnabled();
  });

  it('sends what the last answer was about, so a follow-up can build on it', async () => {
    const calls = mockApi({ [ASK]: fixtures.count });
    renderPanel();
    await ask('How many laptops are available?');
    await screen.findByText('3 laptops');
    await ask('and monitors?');
    await screen.findAllByText('3 laptops');

    const [first, second] = calls.filter((call) => call.path === '/api/assistant/ask');
    expect(first.body.context).toBeNull();
    expect(second.body.context).toEqual({
      intent: fixtures.count.intent,
      slots: fixtures.count.slots,
    });
  });

  it('does not let a refused question replace the context', async () => {
    const replies = [fixtures.count, fixtures.refused, fixtures.count];
    const calls = mockApi({ [ASK]: () => replies.shift() });
    renderPanel();
    await ask('How many laptops are available?');
    await screen.findByText('3 laptops');
    await ask("What's the weather in Durban?");
    await screen.findByText(/outside my supported scope/);
    await ask('and monitors?');
    await screen.findAllByText('3 laptops');

    expect(calls[2].body.context.intent).toBe(fixtures.count.intent);
  });

  it('draws a chart for a trend and a table for a list', async () => {
    const replies = [fixtures.trend, fixtures.list];
    mockApi({ [ASK]: () => replies.shift() });
    renderPanel();

    await ask('Show purchases as a chart');
    const chart = await screen.findByRole('img', { name: fixtures.trend.chart!.note });
    expect(chart.querySelectorAll('rect.column-chart__bar')).toHaveLength(
      fixtures.trend.chart!.rows.length,
    );

    await ask('Show me the available monitors');
    const table = await screen.findByRole('table', { name: 'Results' });
    expect(within(table).getByRole('columnheader', { name: 'Asset no' })).toBeInTheDocument();
    expect(within(table).getAllByRole('row')).toHaveLength(fixtures.list.table!.rows.length + 1);
  });

  it('shows an asset as a card of facts with its recent history', async () => {
    mockApi({ [ASK]: fixtures.asset });
    renderPanel();
    await ask('Tell me about AST-0001');

    const card = await screen.findByRole('region', { name: fixtures.asset.details!.title });
    for (const row of fixtures.asset.details!.rows) {
      expect(within(card).getByText(row.label)).toBeInTheDocument();
    }
    expect(screen.getByRole('table', { name: 'Results' })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: 'Changed on' })).toBeInTheDocument();
  });

  it('offers the full history after an asset card, and shows it as a table', async () => {
    const calls = mockApi({
      [ASK]: (body: any) =>
        body.question.startsWith('Show the history') ? fixtures.timeline : fixtures.asset,
    });
    renderPanel();
    await ask('Tell me about AST-0001');

    await userEvent.setup().click(await screen.findByRole('button', { name: 'Full history' }));
    const tables = await screen.findAllByRole('table', { name: 'Results' });
    const history = tables.at(-1)!;
    for (const name of ['Occurred', 'Event', 'Detail', 'Done by']) {
      expect(within(history).getByRole('columnheader', { name })).toBeInTheDocument();
    }
    expect(calls.at(-1)?.body.question).toBe('Show the history of AST-0001');
  });

  it('draws a ranking as bars and a period of purchases as a table with prices', async () => {
    const replies = [fixtures.ranking, fixtures.purchases];
    mockApi({ [ASK]: () => replies.shift() });
    renderPanel();

    await ask('Which location has the most laptops?');
    const bars = await screen.findByRole('list', { name: fixtures.ranking.chart!.note });
    expect(within(bars).getAllByRole('listitem')).toHaveLength(fixtures.ranking.chart!.rows.length);

    await ask('What did we buy in the last 90 days?');
    const table = await screen.findByRole('table', { name: 'Results' });
    expect(within(table).getByRole('columnheader', { name: 'Price' })).toBeInTheDocument();
    expect(within(table).getAllByText(/^R\d/).length).toBeGreaterThan(0);
  });

  it('offers dashboards as buttons, and a click opens that dashboard in the chat', async () => {
    const calls = mockApi({
      [ASK]: (body: any) =>
        body.question.startsWith('Open') ? fixtures.opened : fixtures.dashboardChoices,
    });
    renderPanel();
    await ask('What dashboards are there?');
    for (const dashboard of fixtures.dashboards) {
      expect(await screen.findByRole('button', { name: dashboard.title })).toBeInTheDocument();
    }

    await userEvent.setup().click(screen.getByRole('button', { name: 'Operational' }));
    expect(await screen.findByText('Purchases by month')).toBeInTheDocument();
    expect(calls.at(-1)?.body.question).toBe('Open the Operational dashboard');
  });

  it('offers a full page for an opened dashboard when the app can show one', async () => {
    mockApi({ [ASK]: fixtures.opened });
    const onOpenDashboard = vi.fn();
    renderPanel({ onOpenDashboard });
    await ask('Open the Operational dashboard');
    await userEvent.setup().click(await screen.findByRole('button', { name: 'Open full page' }));
    expect(onOpenDashboard).toHaveBeenCalledWith('operational');
  });

  it('offers no full page button when the app cannot show one', async () => {
    mockApi({ [ASK]: fixtures.opened });
    renderPanel();
    await ask('Open the Operational dashboard');
    await screen.findByText('Purchases by month');
    expect(screen.queryByRole('button', { name: 'Open full page' })).not.toBeInTheDocument();
  });

  it('shows suggestions under a refusal and asks one when clicked', async () => {
    const calls = mockApi({ [ASK]: fixtures.refused });
    renderPanel();
    await ask("What's the weather in Durban?");
    const chip = await screen.findByRole('button', { name: fixtures.refused.chips[0].label });
    await userEvent.setup().click(chip);
    await screen.findAllByText(/outside my supported scope/);
    expect(calls.at(-1)?.body.question).toBe(fixtures.refused.chips[0].question);
  });

  it('says so, without technical detail, when the server fails', async () => {
    mockApi({ [ASK]: serverError });
    renderPanel();
    await ask('How many laptops are available?');
    expect(
      await screen.findByText('Something went wrong on our side. Try again.'),
    ).toBeInTheDocument();
    expect(screen.queryByText('boom')).not.toBeInTheDocument();
  });

  it('has a close button only in the floating version', async () => {
    const onClose = vi.fn();
    const { unmount } = renderPanel();
    expect(screen.queryByRole('button', { name: 'Close the assistant' })).not.toBeInTheDocument();
    unmount();

    renderPanel({ variant: 'sheet', onClose });
    await userEvent.setup().click(screen.getByRole('button', { name: 'Close the assistant' }));
    expect(onClose).toHaveBeenCalled();
  });
});
