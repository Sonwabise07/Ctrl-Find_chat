import { Icon } from '../components/Icon';
import type { Meta } from '../api/types';
import type { Route } from './routes';

interface NavItem {
  label: string;
  route?: Route;
}

/** Only the three pages built so far are links. The rest show the full menu from the designs. */
const GROUPS: { title: string; items: NavItem[] }[] = [
  { title: 'Overview', items: [{ label: 'Dashboard', route: { page: 'dashboard' } }] },
  { title: 'Asset register', items: [{ label: 'Asset register' }, { label: 'Asset locations' }] },
  {
    title: 'Lifecycle',
    items: [
      { label: 'Onboarding' },
      { label: 'Take-home requests' },
      { label: 'Transfers' },
      { label: 'Emergency swap' },
    ],
  },
  {
    title: 'Operations',
    items: [{ label: 'Stock & storeroom' }, { label: 'Faults & repairs' }, { label: 'Warranty' }],
  },
  {
    title: 'Risk & exit',
    items: [
      { label: 'Loss, theft & AOD' },
      { label: 'Audit & risk' },
      { label: 'Offboarding' },
      { label: 'Disposal' },
    ],
  },
  {
    title: 'Insights',
    items: [
      { label: 'Reports', route: { page: 'reports', tab: 'operational' } },
      { label: 'Data assistant', route: { page: 'assistant' } },
    ],
  },
];

const ROLES: Record<string, string> = {
  fixed_assets: 'Fixed Assets team',
  admin: 'Admin',
  manager: 'Manager',
  employee: 'Employee',
};

interface Props {
  route: Route;
  navigate: (route: Route) => void;
  user?: Meta['user'];
}

export function Sidebar({ route, navigate, user }: Props) {
  return (
    <aside className="sidebar" aria-label="Main navigation">
      <div className="sidebar__brand">
        <span className="sidebar__logo">
          <Icon name="box" />
        </span>
        <div>
          <strong>Asset Hub</strong>
          <small>Fixed Assets</small>
        </div>
      </div>
      <nav>
        {GROUPS.map((group) => (
          <div key={group.title}>
            <p className="sidebar__group">{group.title}</p>
            {group.items.map((item) => {
              const current = item.route?.page === route.page;
              return item.route ? (
                <a
                  key={item.label}
                  className={current ? 'nav-link nav-link--current' : 'nav-link'}
                  href={`#/${item.route.page}`}
                  aria-current={current ? 'page' : undefined}
                  onClick={(event) => {
                    event.preventDefault();
                    navigate(item.route as Route);
                  }}
                >
                  {item.label}
                </a>
              ) : (
                <span key={item.label} className="nav-link nav-link--soon" aria-disabled="true">
                  {item.label}
                </span>
              );
            })}
          </div>
        ))}
      </nav>
      {user && (
        <div className="sidebar__user">
          <span className="sidebar__avatar">{initials(user.name)}</span>
          <div>
            <span>{shortName(user.name)}</span>
            <small>{ROLES[user.role] ?? user.role}</small>
          </div>
        </div>
      )}
    </aside>
  );
}

const initials = (name: string) =>
  name
    .split(' ')
    .map((word) => word[0])
    .join('');

/** "Naledi Mokoena" becomes "N. Mokoena". */
const shortName = (name: string) => name.replace(/^(\S)\S*/, '$1.');
