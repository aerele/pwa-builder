# Learnings — PWA Builder

Living notes from local work on `pwa_builder` / `pwa_build` with Frappe + ERPNext.  
Keep adding points here as more work lands.

---

## 1. Environment (this bench)

| Item | Value |
|------|--------|
| Bench | `/Users/apple/Frappe/frappe-v16-py314` |
| Default site | `pwa.localhost` |
| Web port | `8008` (`sites/common_site_config.json`) |
| Vite (frontend dev) | often `localhost:8080` |
| Desk | `http://pwa.localhost:8008` or `http://127.0.0.1:8008` |
| Builder SPA | `/pwa-builder` |
| Repo remote | `upstream` → `https://github.com/aerele/pwa-builder.git` |
| Default branch | `develop` |

### Useful commands

```bash
cd /Users/apple/Frappe/frappe-v16-py314
bench start
bench --site pwa.localhost list-apps
bench --site pwa.localhost migrate
bench --site pwa.localhost clear-cache
bench build --app pwa_builder

cd apps/pwa_builder/frontend
yarn install
yarn dev      # HMR on Vite port
yarn build    # → pwa_builder/public/frontend + www/frontend.html
```

After frontend changes: rebuild (or use Vite) + hard refresh (**Cmd+Shift+R**).

---

## 2. Architecture (quick)

| App | Role |
|-----|------|
| **frappe** | Framework, auth, REST, Desk |
| **erpnext** | Business DocTypes / data |
| **pwa_builder** | Designer SPA + export/publish API |
| **pwa_build** | Template runtime PWA (cloned/renamed on publish) |

### Flow

1. Design screens in `/pwa-builder` → stored as **PWA DocType** (`field_list` JSON).
2. Publish → clone template → write form JSON → brand → rename app → push GitHub.
3. Install generated app + `migrate` → `after_migrate` imports **PWA Form** records.

### Key DocTypes

- **PWA-Project** — project + connection + branding + GitHub URLs  
- **PWA DocType** — one screen (`field_list`, `nav_order`)  
- **PWA GitHub Integration** — Single DocType (settings in `tabSingles`, **no** list table)  
- **PWA Form / PWA Dashboard** — runtime (from `pwa_build` after migrate)

### Important name spelling

- Correct: **`PWA GitHub Integration`** (capital **H** in Hub)  
- Wrong: `PWA Github Integration` → Desk `get_count` / missing table errors  

Never open a **Single** DocType as List from a workspace shortcut; use Form/URL (e.g. `/desk/pwa-github-integration`).

---

## 3. Frontend structure

```
apps/pwa_builder/frontend/src/
  components/
    LinkField.vue       # Frappe-style link search (search_link)
    PhoneFrame.vue      # Device bezel + scale
  pages/
    project/
      ProjectData.vue   # DocType picker + list
      ProjectScreens.vue
    builder/
      Builder.vue
      components/
        PalettePane.vue
        CanvasPane.vue
        PreviewPane.vue
        PreviewField.vue
        InspectorPane.vue
  design/tokens.css     # Brand / surface / radius CSS variables
```

Route base: `/pwa-builder` (`router.js` + `hooks.py` website_route_rules).

---

## 4. UI / UX patterns learned

### Link / DocType pickers

- **Do not** use native `<datalist>` for DocType pickers (browser dumps entire list; not Frappe-like).
- **Do** use **frappe-ui** when available:
  - `Autocomplete` + `frappe.desk.search.search_link`
  - Reusable wrapper: `LinkField.vue` (HRMS-style Link pattern)
- Style LinkField to **PWA Builder tokens** (`.add__in` / `.nw__in`), not default gray frappe-ui combobox.
- Filters for DocType search: `{ istable: 0, issingle: 0 }`.
- Debounce search ~300ms.

### Phone preview

- Scale the **whole bezel** (padding + screen), not only the screen — outer box must include chrome width/height.
- Flex column + scroll: body needs `flex: 1; min-height: 0; overflow-y: auto`.
- Empty phone state: do **not** apply dashboard 2-col grid when empty; center icon + text with flex.
- Keep preview light (`theme-light` / hard-coded light colors) even if builder is dark.

### Layout / overflow

- Sidebar lists (Insert palette): parent chain needs `min-height: 0` + `overflow: hidden`; list alone scrolls (`overflow-y: auto`).
- Long labels: `text-overflow: ellipsis; white-space: nowrap; min-width: 0`.
- Builder panes grid: `overflow: hidden` on panes row so children cannot spill.

### Dialogs

- Prefer **frappe-ui `Dialog`** over browser `confirm()` / `alert()`.
- Delete: title + danger icon + Cancel (subtle) + Delete (solid red) + loading state.

### Empty states

- Center both axes: icon + text, `text-align: center`, `align-items: center`, `justify-content: center`.
- Apply consistently: phone preview, canvas, screen card mini empty.

---

## 5. Desk / workspace fixtures

When editing DocType / Workspace JSON fixtures:

1. Fix wrong `link_to` names to exact DocType names.
2. Bump **`modified`** to **now** with real microseconds (not `.000000`).
3. Set **`modified_by`** (e.g. `Administrator`).
4. Sync DB workspace rows if the site already has an older workspace document (JSON alone may not reload until migrate/import).
5. Single DocTypes: workspace shortcut `type: URL` → `/desk/<scrubbed-name>` rather than DocType List.

---

## 6. Backend notes (export / API)

| Method | Use |
|--------|-----|
| `pwa_builder.api.add_site` | Create project (This Site / Another Site) |
| `pwa_builder.api.get_meta` | DocType fields for palette |
| `pwa_builder.api.set_value` | Save only `PWA DocType.field_list` |
| `pwa_builder.api.validate_form_fields` | Pre-publish mandatory checks |
| `pwa_builder.api.export_project` | Enqueue publish job |
| `pwa_builder.api.export_status` | Poll job + repo URL |
| `frappe.desk.search.search_link` | Link/DocType typeahead |

Export workdir: `sites/<site>/private/files/<project>/` (not public).

---

## 7. Git / PR conventions (user rules)

### Branch names

- Prefix: **`fix-`** or **`feat-`**
- Use **hyphens only** (`-`)
- **No slashes** (`/`) — e.g. prefer  
  `fix-builder-ui-link-search-and-preview`  
  not `fix/builder-ui-...`
- Renaming a branch that is already a PR head can **close** the old PR; open a new PR on the new branch if needed.

### Commit messages

```
fix: short description of what was fixed
feat: short description of what was added
```

Examples:

- `fix: builder UI link search, preview layout, and panel overflow`
- `feat: add LinkField for DocType typeahead search`

### PR description

- **Do not** invent / require a separate GitHub **Issue** just for the PR.
- **Do not** put “authored by” / “done by AI” style credits.
- **Do** include an **`## Issue`** section with a **paragraph of what was faced** (problem statement in prose).
- Then: Summary, What changed, Screenshots, Test plan.
- Attach shared screenshots (before/after) in the PR body.
- Screenshots can live temporarily on the branch under e.g. `docs/pr-assets/<topic>/` and be linked via raw GitHub URLs for that branch.

### Example PR skeleton

```markdown
## Summary
…

## Issue
While using … [what broke / what felt wrong in product terms].

## What changed
…

## Screenshots (before)
![…](url)

## Test plan
- [ ] …
```

### Remote / `gh`

- This clone uses remote name **`upstream`** for `aerele/pwa-builder`.
- `gh` may need `GH_TOKEN` from git credential helper if not logged in interactively.
- Base branch for PRs: **`develop`**.

---

## 8. PR record — builder UI fixes (2026-07)

| Item | Value |
|------|--------|
| Branch | `fix-builder-ui-link-search-and-preview` |
| Commit | `fix: builder UI link search, preview layout, and panel overflow` |
| PR | https://github.com/aerele/pwa-builder/pull/27 |
| Base | `develop` |

### Problems fixed (Issue paragraph)

DocType selection used a long native browser dropdown without Frappe type-to-search. Phone preview broke/clipped on dense forms; empty state was not centered. Screen delete used browser `confirm()`. Insert palette overflowed (long Number Card names). Desk workspace used wrong GitHub Integration DocType name and List on a Single.

### Files touched (high level)

- `frontend/src/components/LinkField.vue` (new)
- `PhoneFrame.vue`, `PreviewPane.vue`, `PreviewField.vue`
- `PalettePane.vue`, `CanvasPane.vue`, `InspectorPane.vue`, `Builder.vue`
- `ProjectData.vue`, `ProjectScreens.vue`
- `pwa_builder/.../workspace/pwa_builder/pwa_builder.json`
- `docs/pr-assets/fix-builder-ui/*` (before screenshots)

### Screenshots on branch

```
docs/pr-assets/fix-builder-ui/
  01-doctype-datalist-before.jpg
  02-phone-preview-before.jpg
  03-native-delete-confirm-before.jpg
  04-empty-state-off-center-before.jpg
  05-palette-overflow-before.jpg
```

---

## 9. Debugging checklist

| Symptom | Check |
|---------|--------|
| Blank `/pwa-builder` | `yarn build` / Vite; asset 404 in Network tab |
| Stale UI | Hard refresh; clear-cache; confirm Vite vs port 8008 assets |
| Palette empty | `get_meta`, connection type This Site, ERPNext installed |
| Publish blocked | GitHub Integration token; missing mandatory fields |
| Workspace GitHub error | DocType name `PWA GitHub Integration`; not List on Single |
| List item outside panel | Parent `min-height: 0` + list `overflow-y: auto` |
| Phone empty not centered | Disable grid when empty; flex center |
| Push closed PR | Branch deleted/renamed — open new PR on new head |

---

## 10. Keep adding

When new work lands, append:

1. Date / PR or branch name  
2. Issue paragraph (what was faced)  
3. Fix / pattern to reuse  
4. Any convention change (branch, commit, PR, tokens)

---

*Last updated: 2026-07-15 — PR #27 builder UI fixes + PR workflow conventions.*
