import type { KpiData, Tone } from '../../api/types';
import { Icon, type IconName } from '../Icon';
import './widgets.css';

const ICONS: Partial<Record<Tone, IconName>> = {
  info: 'box',
  accent: 'users',
  warn: 'wrench',
  danger: 'alert',
};

interface Props {
  title: string;
  tone: Tone;
  data: KpiData;
}

export function KpiCard({ title, tone, data }: Props) {
  return (
    <section className={`kpi-card kpi-card--${tone}`}>
      <div className="kpi-card__top">
        <span className="kpi-card__icon">
          <Icon name={ICONS[tone] ?? 'box'} />
        </span>
        {data.tag && <span className="kpi-card__tag">{data.tag}</span>}
      </div>
      <p className="kpi-card__value">{data.text}</p>
      <p className="kpi-card__label">{title}</p>
    </section>
  );
}
