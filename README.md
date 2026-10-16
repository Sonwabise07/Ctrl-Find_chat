# Asset Hub Data Assistant

Answers plain-English questions from the Asset Hub database only. Anything the data does not hold gets a clear
"outside my supported scope" reply.

## How a question is handled
1. **Understand.** A local Ollama model picks one supported question type and its filters. If Ollama is not running, a keyword matcher does the same job.
2. **Validate.** Filters must match values that exist in the database (locations, departments, types, statuses). Unknown names are refused, not guessed.
3. **Fetch.** A fixed SQL file runs as a read-only role, limited to what the user's role may see.
4. **Answer.** The reply is built from templates using only the returned rows. A final check rejects any number that is not in the data.

The model never writes SQL, never writes the answer and never sees the database.

## Project layout
```
assistant/
  api.py             HTTP routes
  service.py         one question end to end
  app.py             wires the pieces together
  identity.py        current user and role (demo implementation)
  settings.py        environment settings
  catalog.py         supported question types (config/intents.json)
  vocabulary.py      word lists and fixed messages (config/vocabulary.json)
  understanding/     slot extraction, rule classifier, Ollama classifier, unknown-name check
  queries/           query runner, role scope, date periods
  answers/           one module per kind of result, plus the number check
  data/              database connection and lookups
  dashboards/        dashboard definitions, widget shaping and the dashboard service
  config/            intents.json, vocabulary.json, dashboards.json
  sql/               one SQL file per question type
  sql/metrics/       one SQL file per dashboard widget
web/index.html       the original plain chat page, served by the backend on port 8000
web-react/           the React screen (chat, charts, dashboards). See web-react/README.md
db/                  schema, dummy data, proposed migration, read-only role
tests/               unit/ (no database), integration/ (HTTP API against the database),
                     prompts.json and try_prompts.py (121 test questions to run by hand or in bulk)
```
Adding a question type: add `sql/<name>.sql`, an entry in `config/intents.json`, a routing phrase in `config/vocabulary.json`, and a formatter in `answers/`.

## Run it
Needs PostgreSQL, Python 3.10+ and optionally Ollama.
```
createdb asset_hub
psql -d asset_hub -f db/schema.sql
psql -d asset_hub -f db/seed.sql
psql -d asset_hub -f db/proposed_migration.sql   # optional: enables audit and AOD questions
psql -d asset_hub -f db/seed_proposed.sql        # only if the migration was applied
psql -d asset_hub -f db/roles.sql                # run again after any migration
pip install -r requirements.txt
ollama pull llama3.2:3b                          # optional
python -m assistant                              # then open http://localhost:8000
```
Settings (environment variables): `DATABASE_URL`, `OLLAMA_URL`, `OLLAMA_MODEL`, `CLASSIFIER` (`auto`, `ollama` or `rules`), `PORT`.
Without the migration, audit and AOD questions reply that the information is not held, and the side panel shows them as unavailable.
Demo users: `/?as=thandi.nkosi@example.co.za` (employee), `/?as=sipho.dlamini@example.co.za` (manager). The default is Fixed Assets.

## React screen
```
cd web-react
npm install
npm run dev        # http://localhost:5173, with the backend running on port 8000
npm test
```
Details, and how to move it into the main React app, are in `web-react/README.md`.

## Tests
Backend (195 tests):
```
pip install -r requirements-dev.txt
set ADMIN_DSN=postgresql://postgres:<password>@localhost/asset_hub    (PowerShell: $env:ADMIN_DSN="...")
pytest
```
`ADMIN_DSN` is a user that can read every table. It is only used to work out the expected figures.
Integration tests call the HTTP API, so they can check another implementation: set `ASSISTANT_URL=http://host:port` and run `pytest tests/integration`.
Tests that need a fake Ollama are skipped in that mode.

To try all 121 sample questions against a running assistant and see each answer: `python tests/try_prompts.py` (`--group refused` runs one group). It reports any reply that is not the expected question type.

## API contract
`POST /api/assistant/ask`
```
request   { "question": string, "context": { "intent": string, "slots": object } | null, "as": string | null }
response  { "scope": "in" | "out", "answer": string, "intent": string | null, "classifier": "ollama" | "rules" | null,
            "slots": object | null, "source": string | null,
            "chart": { "kind": "bars" | "columns", "rows": [{ "label", "value", "text" }], "note" } | null,
            "table": { "columns": string[], "rows": object[] } | null,
            "details": { "title", "rows": [{ "label", "text" }] } | null,
            "dashboard": { "id", "title", "widgets": [...] } | null,
            "chips": [{ "label", "question" }] }
```
`GET /api/assistant/meta` returns `{ chips, categories: [{ label, available }], user: { name, role } }`.
`answer` uses `**bold**` markers. `context` is the `intent` and `slots` of the previous in-scope reply, which enables follow-ups such as "and laptops?".
The `as` field is a demo shortcut and must not exist in the main system. The user comes from the login.

## Asset lookup, rankings, date ranges and asset age
- **Asset lookup:** "Tell me about AST-0013", "Who has AST-0001?", "serial number ...". Returns a facts card (`details`) and the five latest history events (`table`). The asset number can be typed any way (`ast0013`, `AST-0013`) and is matched on the asset number, serial number or tracking number, always inside the user's own access.
- **Rankings:** "Which location has the most laptops?", "Top 3 departments by asset value", "Which asset type is the most expensive?". By location, department, type or status, by count or by purchase value, most or fewest, top N (default 5). Assets with no value for the group (for example no department) are left out.
- **Date ranges:** "What did we buy in the last 90 days?", "How many repairs were reported this quarter?", "bought between July and September". These cover purchases (by purchase date) and repairs (by reported date). The answer always states the exact dates it used.
- **Asset age:** "laptops older than 3 years". Works with counts, lists, splits, rankings and purchases. Age is measured from the purchase date.

Limits, stated in the replies rather than hidden:
- A date range on any other question, and a ranking inside a date range, get a plain explanation instead of an answer that ignores the date.
- Asset numbers must be 2 to 5 letters followed by digits (for example `AST-0013`), or a serial number after the word "serial".
- A period with no year means its most recent occurrence ("in December" in October means last December).

## Your assets, asset history, leavers and cases
- **My assets:** "What am I responsible for?", "Show my laptops". Always the assets assigned to the person asking, whatever their role.
- **My team's assets:** "Show my team's assets". The team is taken as the person's department, because the database has no manager link yet. The reply says so. What they see still follows their role.
- **Asset history:** "Show the history of AST-0013", "what happened to AST-0013?", or "show its history" after an asset card (the card also offers a "Full history" button). It merges the permanent history log, repairs, and, when those tables exist, audit confirmations and loss cases. Newest first, latest 40.
- **Assets still held by people who left:** "Which assets are still held by people who have left?" Assets assigned to people marked inactive, laptops first. The database has no exit dates or offboarding cases yet, so this is an approximation, and the reply says so.
- **Loss, theft and AOD cases:** "Show open loss and theft cases", "Who has an open AOD?". These need the proposed migration. They show employee names and amounts, so they should be limited by role before real use.
- **Laptop age and warranty:** "How old are our laptops?" Age, warranty end, and how many laptops are past warranty or end within 90 days. There are no health colours, because the requirements do not define the thresholds.
- **Spare stock by location:** "Show spare stock by location" now splits by location (it used to split by type).

The dummy data in `db/seed.sql` now has a realistic permanent history (registrations, assignments, returns) and two people marked inactive who still hold assets. Reload the database to see it.

## Dashboards
Charts and dashboards come from the same data under the same rules: fixed SQL, the role access filter, and the read-only role.
Users cannot write their own queries. A dashboard is a list of widgets in `config/dashboards.json`, each pointing at one SQL file.

`GET /api/dashboards` returns `[{ "id", "title" }]`. `GET /api/dashboards/{id}` returns
```
{ "id", "title", "widgets": [{ "id", "type", "title", "size", "available": bool, "data": ... }] }
```
Widget types and their `data`:

| Type | Draws | `data` |
|---|---|---|
| `kpi` | A number card (extra field `tone`) | `{ value, text, tag }` |
| `bars` | Horizontal bars with a share of the total | `{ total, rows: [{ label, value, text, share }] }` |
| `columns` | Vertical bars over time | `{ rows: [{ label, value, text }] }` |
| `table` | A table | `{ columns: [{ key, title }], rows: [{ key: text }] }` |
| `list` | An alerts list | `{ rows: [{ title, subtitle, tone }] }` |
| `trends` | This month against last month | `{ rows: [{ label, text, previous_text, direction, change, tone }] }` |
| `keyvalue` | Label and value pairs | `{ rows: [{ label, text }] }` |

`size` is a layout hint (`small`, `medium`, `full`). `available` is false when a table the widget needs does not exist yet, and `data` is then null.
Dashboards: `overview`, `operational`, `management`. The audit and AOD widgets need the proposed migration.

**In the chat**
- "What dashboards are there?" lists the dashboards as buttons (the reply's `chips`). A button sends "Open the <name> dashboard", which returns that dashboard in the reply's `dashboard` field. Naming a dashboard in the question opens it directly.
- "Show purchases as a chart" or "Show the repair cost trend" returns a chart of change over time (`kind: columns`). Topics are listed under `chart_topics` in `config/dashboards.json`: each points at a dashboard widget and the words that ask for it.
- "Show this as a chart" after an answer draws the chart that belongs to it. After a cost comparison or warranty list it is the trend over time. After a count or list it is a split of the same assets by a column the question did not already fix (`kind: bars`).
- A trend chart cannot apply filters such as "for laptops". It says so in the source line.
- If there is nothing to chart, the reply says what can be charted.

Adding a widget: write `sql/metrics/<name>.sql` that reads from `scoped`, return the columns its type expects (see the existing files), then add an entry to `config/dashboards.json`.

## Moving into the main .NET system
| Here | In the main system |
|---|---|
| `api.py` | `AssistantController` and `DashboardsController` with the routes above, protected by the existing authorisation |
| `service.py` | `AssistantService` |
| `identity.py` | An `ICurrentUser` that reads the user id, department and role from the login. Map role names to `fixed_assets`, `admin`, `manager`, `employee` |
| `understanding/` | `IIntentClassifier` with Ollama and rule implementations, plus the slot extractor |
| `queries/`, `dashboards/` | `QueryRunner` and `DashboardService`. Keep the `scoped` CTE in front of every query |
| `answers/` | One formatter per question type, plus the number check |
| `config/*.json`, `sql/*.sql` | Copy as they are (embedded resources) |
| `web/index.html` | React components. Reuse the shared colours and shell instead of the sidebar here |
| `db/roles.sql` | Run on the real database. The assistant must connect with this read-only role |

Run `tests/integration` against the new endpoint with `ASSISTANT_URL` to prove it gives the same answers.

## Known limits
- Make and model are not columns in the schema, so "Dell laptops" is matched on the description text.
- Maintenance status values are assumed to be `Open`, `In Progress` and `Completed`.
- Chat history lives in the browser only.
- Ollama has only been tested here with a stand-in. Test the real model with your own wording.
