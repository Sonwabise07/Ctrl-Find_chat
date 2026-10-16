# Asset Hub Data Assistant: React screen

The chat, charts and dashboards for the Data Assistant, built with React and TypeScript.
No UI library and no chart library: the charts are small SVG and HTML components styled with the Asset Hub colours.

## Run it
Needs Node 20 or newer and the assistant backend running on port 8000 (`python -m assistant` in the project folder).
```
cd web-react
npm install
npm run dev          # http://localhost:5173
```
The dev server forwards `/api` to `http://localhost:8000`, so no extra setup is needed.
Demo users work as before: `http://localhost:5173/?as=thandi.nkosi@example.co.za`.

| Command | Does |
|---|---|
| `npm run dev` | Development server with live reload |
| `npm test` | 59 tests (Vitest and Testing Library) |
| `npm run typecheck` | TypeScript check |
| `npm run build` | Type check, then a production build in `dist/` |
| `npm run format` | Prettier |

## What is in it
```
src/
  api/types.ts          the API shapes (keep in step with the API contract in the main README)
  api/client.ts         fetch calls. The only file that talks to the network
  components/
    charts/             BarList (groups), ColumnChart (over time), ChartView (picks one)
    widgets/            one component per widget type, and WidgetRenderer that picks by type
    dashboard/          DashboardView: the widget grid
    chat/               ChatPanel, useChat, message components, SupportedTypes
    DataTable.tsx, Icon.tsx
  shell/ and pages/     PROTOTYPE ONLY: sidebar, header, hash routing and the three pages
  styles/tokens.css     the design colours as CSS variables
  test/                 fixtures captured from the real backend, and a fetch mock
```

## How it fits together
- `useChat` keeps the conversation and sends the previous question type with each question, so follow-ups such as "and laptops?" and "show this as a chart" work.
- A chat reply can carry text, a chart, a table, a facts card (an asset) and a whole dashboard. `AssistantMessage` draws each part that is present.
- Dashboard choices come back as suggestion buttons. Clicking one asks "Open the ... dashboard".
- `WidgetRenderer` draws a dashboard widget by its `type`. A widget whose tables do not exist yet shows a plain note.
- Charts: one colour, because position and length carry the meaning. `ColumnChart` labels only the highest column and every other month when there are many. Hover shows each value.

## Moving into the main React app
Copy these:
- `src/components/` (the whole folder), `src/api/types.ts`, `src/utils/`
- `src/styles/tokens.css`, and map the variables to the main theme. The components only use these variables.

Replace these:
- `src/api/client.ts`: use the main app's HTTP layer, so requests carry the login token. Remove the `?as=` demo shortcut. The user comes from the login.

Do not copy:
- `src/shell/` and `src/pages/`: they are a stand-in for the main app's layout and router. From them, reuse `DashboardBody`, `FloatingChat` and the way `ChatPanel` and `SupportedTypes` are placed in `AssistantPage`.
- Wire `onOpenDashboard` to the main router. The prototype sends Overview to Dashboard and Operational and Management to the Reports tabs (`routeForDashboard`).

Styles are plain CSS files next to each component, with class names like `chat__input` and `kpi-card`. If the main app uses CSS modules or another system, port them component by component.

## Known limits
- The Python backend is still the prototype. These screens use only the documented API, so they work unchanged with the .NET version.
- The sidebar shows the full menu from the designs, but only Dashboard, Reports and Data assistant are pages so far.
- Fixtures in `src/test/fixtures/` are saved backend replies. Refresh them if the API changes.
