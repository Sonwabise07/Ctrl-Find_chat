import { Icon } from '../components/Icon';

export function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header className="page-header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="page-header__tools">
        <div className="page-header__search">
          <Icon name="search" />
          Search assets, employees...
        </div>
        <button type="button" className="page-header__bell" aria-label="Notifications">
          <Icon name="bell" />
        </button>
      </div>
    </header>
  );
}
