import type { Dashboard, DashboardSummary, Meta, Reply } from '../api/types';
import dashboardManagement from './fixtures/dashboard-management.json';
import dashboardOperational from './fixtures/dashboard-operational.json';
import dashboardOverview from './fixtures/dashboard-overview.json';
import dashboards from './fixtures/dashboards.json';
import meta from './fixtures/meta.json';
import replyAsset from './fixtures/reply-asset.json';
import replyCompare from './fixtures/reply-compare.json';
import replyCount from './fixtures/reply-count.json';
import replyDashboards from './fixtures/reply-dashboards.json';
import replyList from './fixtures/reply-list.json';
import replyOpen from './fixtures/reply-open.json';
import replyPurchases from './fixtures/reply-purchases.json';
import replyRanking from './fixtures/reply-ranking.json';
import replyTimeline from './fixtures/reply-timeline.json';
import replyRefused from './fixtures/reply-refused.json';
import replySplit from './fixtures/reply-split.json';
import replyTrend from './fixtures/reply-trend.json';

/** Real replies captured from the backend, so the tests use the actual API format. */
export const fixtures = {
  meta: meta as unknown as Meta,
  dashboards: dashboards as DashboardSummary[],
  overview: dashboardOverview as unknown as Dashboard,
  operational: dashboardOperational as unknown as Dashboard,
  management: dashboardManagement as unknown as Dashboard,
  count: replyCount as unknown as Reply,
  split: replySplit as unknown as Reply,
  list: replyList as unknown as Reply,
  trend: replyTrend as unknown as Reply,
  compare: replyCompare as unknown as Reply,
  dashboardChoices: replyDashboards as unknown as Reply,
  opened: replyOpen as unknown as Reply,
  refused: replyRefused as unknown as Reply,
  asset: replyAsset as unknown as Reply,
  ranking: replyRanking as unknown as Reply,
  timeline: replyTimeline as unknown as Reply,
  purchases: replyPurchases as unknown as Reply,
};
