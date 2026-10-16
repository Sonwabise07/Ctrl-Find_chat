import type { Reply } from '../../api/types';
import { humanise } from '../../utils/format';
import { RichText } from '../../utils/richText';
import { ChartView } from '../charts/ChartView';
import { DashboardView } from '../dashboard/DashboardView';
import { DataTable } from '../DataTable';
import { KeyValueList } from '../widgets/KeyValueList';
import { Suggestions } from './Suggestions';

interface Props {
  reply: Reply;
  onAsk: (question: string) => void;
  /** When given, an opened dashboard gets an "Open full page" button. */
  onOpenDashboard?: (id: string) => void;
}

export function AssistantMessage({ reply, onAsk, onOpenDashboard }: Props) {
  const { chart, table, details, dashboard } = reply;
  const wide = Boolean(chart || table || details || dashboard);
  return (
    <>
      <div className={wide ? 'bubble bubble--assistant bubble--wide' : 'bubble bubble--assistant'}>
        <p className="bubble__text">
          <RichText text={reply.answer} />
        </p>
        {reply.source && <p className="bubble__source">{reply.source}</p>}
        {details && (
          <section className="details-card" aria-label={details.title}>
            <h3>{details.title}</h3>
            <KeyValueList rows={details.rows} />
          </section>
        )}
        {chart && <ChartView chart={chart} />}
        {table && (
          <DataTable
            columns={table.columns.map((key) => ({ key, title: humanise(key) }))}
            rows={table.rows}
            label="Results"
          />
        )}
        {dashboard && (
          <>
            <DashboardView dashboard={dashboard} compact />
            {onOpenDashboard && (
              <button
                type="button"
                className="bubble__action"
                onClick={() => onOpenDashboard(dashboard.id)}
              >
                Open full page
              </button>
            )}
          </>
        )}
      </div>
      <Suggestions chips={reply.chips} onAsk={onAsk} />
    </>
  );
}
