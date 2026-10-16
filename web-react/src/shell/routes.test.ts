import { parseRoute, routeForDashboard, routeHash } from './routes';

describe('routes', () => {
  it('reads the page and tab from the hash', () => {
    expect(parseRoute('')).toEqual({ page: 'dashboard' });
    expect(parseRoute('#/assistant')).toEqual({ page: 'assistant' });
    expect(parseRoute('#/reports/management')).toEqual({ page: 'reports', tab: 'management' });
    expect(parseRoute('#/reports')).toEqual({ page: 'reports', tab: 'operational' });
    expect(parseRoute('#/nonsense')).toEqual({ page: 'dashboard' });
  });

  it('writes a route back to a hash', () => {
    expect(routeHash({ page: 'reports', tab: 'management' })).toBe('#/reports/management');
    expect(routeHash({ page: 'dashboard' })).toBe('#/dashboard');
  });

  it('sends each dashboard to the page that shows it in full', () => {
    expect(routeForDashboard('overview')).toEqual({ page: 'dashboard' });
    expect(routeForDashboard('operational')).toEqual({ page: 'reports', tab: 'operational' });
    expect(routeForDashboard('management')).toEqual({ page: 'reports', tab: 'management' });
  });
});
