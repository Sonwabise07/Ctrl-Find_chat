/** The shapes the assistant API returns. Keep in step with the API contract in the main README. */

export type Tone = 'info' | 'warn' | 'accent' | 'danger' | 'good' | 'bad' | 'neutral';

export interface Chip {
  label: string;
  question: string;
}

export interface ChartRow {
  label: string;
  value: number;
  text: string;
  share?: number;
}

export interface Chart {
  kind: 'bars' | 'columns';
  rows: ChartRow[];
  note: string;
}

export interface Details {
  title: string;
  rows: { label: string; text: string }[];
}

/** A table in a chat reply: columns are plain keys such as `asset_no`. */
export interface ReplyTable {
  columns: string[];
  rows: Record<string, string>[];
}

export interface Reply {
  scope: 'in' | 'out';
  answer: string;
  intent: string | null;
  classifier: string | null;
  slots: Record<string, unknown> | null;
  source: string | null;
  chart: Chart | null;
  table: ReplyTable | null;
  /** Facts about one thing, such as an asset. */
  details: Details | null;
  dashboard: Dashboard | null;
  chips: Chip[];
}

/** What the next question needs to know about the last answer, so "and laptops?" works. */
export interface Context {
  intent: string | null;
  slots: Record<string, unknown> | null;
}

export interface AskRequest {
  question: string;
  context: Context | null;
  as?: string;
}

export interface Meta {
  chips: Chip[];
  categories: { label: string; available: boolean }[];
  user: { name: string; role: string };
}

export interface KpiData {
  value: number;
  text: string;
  tag: string | null;
}
export interface BarsData {
  total: number;
  rows: ChartRow[];
}
export interface ColumnsData {
  rows: ChartRow[];
}
export interface TableData {
  columns: { key: string; title: string }[];
  rows: Record<string, string>[];
}
export interface AlertsData {
  rows: { title: string; subtitle: string; tone: Tone }[];
}
export interface TrendsData {
  rows: {
    label: string;
    text: string;
    previous_text: string;
    direction: 'up' | 'down' | 'flat';
    change: string;
    tone: Tone;
  }[];
}
export interface KeyValueData {
  rows: { label: string; text: string }[];
}

export type WidgetSize = 'small' | 'medium' | 'full';

interface WidgetBase {
  id: string;
  title: string;
  size: WidgetSize;
  /** False when the tables the widget needs do not exist yet. `data` is then null. */
  available: boolean;
}

export type Widget =
  | (WidgetBase & { type: 'kpi'; tone: Tone; data: KpiData | null })
  | (WidgetBase & { type: 'bars'; data: BarsData | null })
  | (WidgetBase & { type: 'columns'; data: ColumnsData | null })
  | (WidgetBase & { type: 'table'; data: TableData | null })
  | (WidgetBase & { type: 'list'; data: AlertsData | null })
  | (WidgetBase & { type: 'trends'; data: TrendsData | null })
  | (WidgetBase & { type: 'keyvalue'; data: KeyValueData | null });

export interface DashboardSummary {
  id: string;
  title: string;
}

export interface Dashboard extends DashboardSummary {
  widgets: Widget[];
}
