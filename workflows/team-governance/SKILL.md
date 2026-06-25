---
name: team-governance
description: Configure your project team, platform tools, and member accounts to generate a team governance document. Use when setting up a new project team or updating team tool configuration.
---

# Team Governance

## Overview

Configure project team members, platform tools, and account IDs to produce a structured `governance.md` file at `{project-root}/{workflow.governance_dir}/governance.md`. Use at project start or whenever team composition or tool configuration changes.

## Conventions

- Bare paths (e.g. `references/file.md`) resolve from `{skill-root}` (where `customize.toml` lives); `{project-root}`-prefixed paths resolve from the project working directory.
- `{workflow.<name>}` resolves to fields in the merged `customize.toml` `[workflow]` table.
- `{skill-root}/governance-session.json` is the active session file — routing is driven by its `current_step` field. Its presence indicates an in-progress configuration run.
- `{project-root}/{workflow.governance_dir}/governance.md` is the output file and source of truth for project resources and team members.

## On Activation

1. Resolve customization: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow`. On failure, read `{skill-root}/customize.toml` directly and use defaults.
2. Execute each entry in `{workflow.activation_steps_prepend}` in order.
3. Treat every entry in `{workflow.persistent_facts}` as foundational context. Entries prefixed `file:` are paths or globs under `{project-root}` — load their contents; others are facts verbatim.
4. Load reference files — read `references/tools-reference.md`, `references/team-roles-reference.md`, and `references/team-governance-schema.md` in full. If any cannot be read, stop with: ⚠ Could not read `{filename}`. Check the path and try again.
5. Detect mode. **Headless** when: no TTY, programmatic caller, `activation_steps_prepend` declares headless, or first message pre-supplies all required inputs. If headless: load `references/headless.md` and follow it for the entire run.
6. Load `{project-root}/_bmad/core/config.yaml` (and `config.user.yaml` if present); resolve `{user_name}`, `{communication_language}`. Missing → neutral defaults; never block.

Execute each entry in `{workflow.activation_steps_append}` in order.

Activation is complete. Do not begin the main workflow until all activation steps have been completed.

## Locate or Create

**Check for an in-progress session**

Try to read `{skill-root}/governance-session.json`. If found and valid JSON, display:
```
Resuming session — step: {current_step}
```
Ask: > Resume, or start fresh? (resume / new)

- **resume:** load `current_step` from session. Read and parse `{project-root}/{workflow.governance_dir}/governance.md` if it exists. Route by `current_step`:

  | `current_step` | Route |
  |---|---|
  | `"resources"` | Project Resources — restore from `pending_tools` / `pending_resources` in session. Skip per-tool collection for tools already in `pending_tools`; resume at the first tool not yet collected. If all selected tools are in `pending_tools`, go to Confirm and Write. The tool selection prompt is not re-displayed on resume — to change the tool list the user must start a new session. |
  | `"members"` | Action menu — the user picks which member action to continue. |
  | `"review"` | Review & Finalize. |

  Resuming at `"members"` always returns to the action menu. The action menu re-reads `governance.md` before displaying the header.

- **new:** delete `governance-session.json`. Proceed to Check for governance.md.

If no session exists, proceed to Check for governance.md.

---

**Check for governance.md**

Try to read `{project-root}/{workflow.governance_dir}/governance.md`.

**Found:** parse it into memory — Project Resources table, Team Members table, Constraints section. Write session `{ "current_step": "resources" }`. Go to **Action menu**.

**Not found:** starting a new governance file. Write session `{ "current_step": "resources" }`. Go to **Action menu**.

---

**Action menu**

Always shown — for both new and existing files. Always re-reads `governance.md` (if it exists) before rendering the header, so counts and tool lists are current.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  governance.md
  {n} members · {tools or "no tools yet"}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
What do you want to do?
  1  {Set up | Update} project resources{  ← start here  (if no tools yet)}
  2  Register multiple members
  3  Update my own info
  4  Edit a specific member{              (no members yet)}
  5  Review & finalize
```

Options 4 and 5 show `(no members yet)` as a hint if `members` is empty. If picked anyway: > No members yet — add at least one member first via option 2 or 3.

Write session before routing — overwrite the full session, clearing any `pending_tools` or `pending_resources` left from a previous interrupted run. `current_step` by choice:

| Choice | `current_step` | Route |
|---|---|---|
| 1 | `"resources"` | Project Resources (loops at Tool selection until enter). New file → action menu after; existing file → Review & Finalize after |
| 2 | `"members"` | Register Multiple Members → Review & Finalize |
| 3 | `"members"` | Update My Info → action menu |
| 4 | `"members"` | Single-edit → Review & Finalize |
| 5 | `"review"` | Review & Finalize |

**If `governance.md` does not exist when a member-related choice (2, 3, or 4) is made:** create it immediately using the template from `references/team-governance-schema.md` with empty Project Resources and Team Members tables (header row only, no tool account columns yet). Then proceed with the chosen action.

## Project Resources

**Source of truth:** `{project-root}/{workflow.governance_dir}/governance.md` Project Resources table. All changes write to that file immediately on confirmation. Before `governance.md` exists, changes buffer in the session under `pending_tools` and `pending_resources`.

---

**Tool selection**

**New file (no existing resources):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Project Resources
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Which tools does your team use?
  1  Jira
  2  GitHub
  3  Figma
  4  Slack
  5  Confluence
  6  Linear
  7  Notion
  8  Environments  (staging / production URLs)
  9  Other         (custom tool)

Enter numbers separated by spaces, or "all":
```

At least one tool must be selected for a new file. Pressing enter alone without a selection is not valid — re-display the prompt.

**Existing file (has resources):**

Show current resources with status, then offer targeted updates:
```
  Current resources:
    ✓ Jira    workspace: myorg · project: RP
    ✓ GitHub  myorg/my-repo
    ⚠ Slack   channel missing

Add a tool or fix a gap? (tool names or numbers space-separated, or press enter to skip)
```

Pressing enter exits this section: write session `{ "current_step": "review" }` and go to Review & Finalize — whether or not there are `⚠` gaps (gaps will appear in Review & Finalize and can be fixed from there).

After per-tool input collection and confirmation, return here so the user can add more tools or press enter to exit.

---

**Per-tool input collection**

For each selected tool, show its inputs one at a time. Read prompt labels and `extracts` field names from `references/tools-reference.md` for the selected tool. After each tool's inputs are confirmed, write the tool slug and collected values to the session as `pending_tools` and `pending_resources`.

```
── Jira ──────────────────────────────────────────────
  Project URL:                    →
  Cloud ID (optional):            →

── GitHub ────────────────────────────────────────────
  Repository URL:                 →

── Slack ─────────────────────────────────────────────
  Workspace URL (optional):       →
  Main channel name (without #):  →
```

For URL fields: extract identifiers in context of the known tool using the `extracts` field names defined in `references/tools-reference.md`.

For **Environments** (option 8):
```
── Environments ──────────────────────────────────────
  Staging URL (primary):          →
  Staging URL (secondary, opt):   →
  Production URL:                 →
```

For **Other** (option 9):
```
Tool name:                        →
Does each member have an account? (yes / no)
```
- **yes:** ask `Account field label (e.g. "email", "username"):` — adds a member column.
- **no:** project-level only — no member column.

Slug generated as: lowercase name, spaces → underscores.

---

**Confirm and write**

```
  Project Resources — confirmed
  ✓ Jira    workspace: myorg · project: RP
  ✓ GitHub  myorg/my-repo
  ⚠ Slack   channel missing

Looks good? (yes / re-enter {tool name})
```

If re-entering a tool: repeat per-tool input for that tool only, then show this summary again.

**On yes:**

- If `governance.md` does not exist: create it now using the template from `references/team-governance-schema.md`. Write the Project Resources table and the Team Members table header (columns = Name, Role, Reviewer, Hours/Day, {account columns for all tools with non-empty `member_inputs` in `references/tools-reference.md`, plus any custom tools with `has_member_accounts: yes`}, Notes). Write Constraints section as empty.
- If `governance.md` exists: patch the Project Resources table rows. Match rows by tool slug — replace matched rows, append new tool rows. If new tools with account columns were added, insert their column into the Team Members table header and fill existing member rows with empty cells.

Remove `pending_tools` and `pending_resources` from the session.

Then route based on mode:
- **New file** (governance.md did not exist before this step): write session `{ "current_step": "members" }`, return to **action menu**.
- **Update mode** (governance.md already existed): write session `{ "current_step": "review" }`, return to **Tool selection** so the user can add more tools or press enter to exit to Review & Finalize.

## Team Members

**Source of truth:** `{project-root}/{workflow.governance_dir}/governance.md` Team Members table. Every member save writes a row to that table immediately. The accounts section of every member card reflects the current tool columns in the table.

---

**Register Multiple Members (action menu choice 2)**

Show existing members from `governance.md` to avoid duplicates:
```
Already registered: Anderson, Luis  (or "none yet")
```

Then:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Register Multiple Members
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Paste a list — one member per line:
  Name, Role
  Name — Role
  Name (Role)
  Name only  (role asked during preview)

Or paste a table: Name | Role | Hours | {tool column} | ...
  (columns can be in any order; unrecognized columns are ignored)
```

Process:

1. Parse Name and Role from each line. Map Role using `references/team-roles-reference.md` aliases (case-insensitive).
2. Show parsed preview:
   ```
   Parsed:
     ✓  Anderson Monroy  →  tech_lead
     ✓  Luis Perez       →  senior_developer
     ⚠  Sara             →  no match for "Sr UX" — clarify:  →
   ```
3. Resolve all `⚠` roles inline before continuing.
4. Apply defaults: `hours = {workflow.default_hours_per_day}`, Reviewer per `reviewer_default` in `references/team-roles-reference.md`, `notes = ""`.
5. Collect accounts — one batched prompt per tool that has an account column in `governance.md`, skipping members who already have a value for that column:
   ```
   ── Jira accounts ──────────────────────────────────
     Anderson   Jira account ID →
     Luis       Jira account ID →
   ── GitHub accounts ────────────────────────────────
     Anderson   GitHub username →
   ```
   Leave blank to skip.
6. After each tool's batch prompt is confirmed, immediately update that column's cells for all members in `governance.md`. Do not wait until all tools are done — write after each tool batch. If the write fails, stop: `⚠ Could not save accounts to governance.md. Check disk space and permissions, then try again.` Do not proceed to the next tool until the write succeeds.
7. After the last member:
   > {n} members saved. Proceed to review? (yes / add more)
   - **yes:** write session `{ "current_step": "review" }`, go to Review & Finalize.
   - **add more:** session remains `{ "current_step": "members" }` — return to the paste prompt.

---

**Update My Info (action menu choice 3)**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Update My Info
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Your name (or partial match):  →
```

- **Exact match** in `governance.md`: show full member card with current values pre-filled.
- **Multiple partial matches:** list them and ask the user to pick one by number.
- **Single partial match:** show that member's card.
- **No match:** treat as a new member — fresh card from Name.

Press enter to keep any field's current value, or type to replace.

After saving: write/update the member row in `governance.md`. Confirm: `✓ {Name} saved.`

Then ask:
```
  Go to review → "review"
  Update more  → enter
```
- **review:** write session `{ "current_step": "review" }`, go to Review & Finalize.
- **enter:** return to action menu.

---

**Member card (used in single-edit and Update My Info):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {Member name | New member}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name              →  (current: {value})
Role              →  (current: {value}) — freeform, mapped automatically
Hours/day         →  (current: {value}, default: {workflow.default_hours_per_day})
Reviewer          →  (current: {value}, default per role)
Notes             →  (current: {value}) — optional
── Platform accounts ──────────────────────────────────
  {Tool label}    {field prompt}   (current: {value or —}) →
  ...
  Press enter to keep current value, or type to replace.
```

Account fields are determined from the `governance.md` Team Members table column headers. Any column that is not one of the five standard fields (Name, Role, Reviewer, Hours/Day, Notes) is treated as an account field and shown in the accounts section.

**Role mapping:** look up input against `aliases` in `references/team-roles-reference.md`, case-insensitive. Confirm: `Role → tech_lead ✓`. No match: offer closest, or store as `"other"`.

**Reviewer default:** check `reviewer_default.yes` list in `references/team-roles-reference.md`. User can override.

**On save:** write/update the member's row in `governance.md` — replace row if name matches existing, append if new.

---

**Single-edit (action menu choice 4):**

List members from `governance.md`:
```
Current members:
  1. Anderson Monroy — tech_lead
  2. Luis Perez — senior_developer

Enter a number to edit, "new" to add, or "done" to finish:
```

- **Number:** show the full member card for that member with current values pre-filled. On save, write the updated row to `governance.md` and return to the member list.
- **"new":** show a fresh member card. On save, append the new row to `governance.md` and return to the member list.
- **"done":** write session `{ "current_step": "review" }`, go to Review & Finalize.

## Review & Finalize

Read `{project-root}/{workflow.governance_dir}/governance.md` and display a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  governance.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
| Name | Role | Rev | Hrs | Jira | GitHub | Notes |
|------|------|-----|-----|------|--------|-------|
| Anderson | tech_lead | ✓ | 8 | 712020:abc | andersonm | |
| Luis | senior_developer | ✓ | 8 | ⚠ | luisp | |

⚠ Missing accounts: Luis → Jira

Constraints: {text or "(none)"}
```

```
What do you want to do?
  • Edit a member          → name or number
  • Add a member           → "new"
  • Remove a member        → "remove {name}"
  • Fill missing accounts  → "fill"
  • Update resources       → "resources"
  • Edit constraints       → "constraints"
  • Done                   → "done" or any affirmative
```

**Routing:**

- **Edit / Add:** show member card. On save, write row to `governance.md`. Re-display summary.
- **Remove:** delete member row from `governance.md`. Re-display summary.
- **Fill missing accounts:** for each account-field column that has at least one empty cell, show the batched account prompt (same format as Register Multiple Members accounts collection), listing only members who have an empty cell for that column. Write updated rows. Re-display summary.
- **Update resources:** write session `{ "current_step": "resources" }`, go to Tool selection. Session is restored to `{ "current_step": "review" }` when the user exits Tool selection (pressing enter), at which point control returns here. If interrupted inside Project Resources, resume correctly returns to Project Resources.
- **Edit constraints:**
  ```
  Constraints (press enter to clear):
  Current: {value or "(none)"}
  →
  ```
  Write Constraints section in `governance.md`. Session is not modified — user remains at `current_step: "review"`. Re-display summary.
- **Done:** proceed to Finalize.

## Finalize

`governance.md` is already up to date — no bulk write needed.

1. Delete `{skill-root}/governance-session.json`. If deletion fails: ⚠ Could not delete governance-session.json — remove it manually to avoid a stale resume prompt next run.

2. Build and return:

   `project_resources` — parse from `governance.md` Project Resources table as a flat key-value object. Keys must be the machine-readable identifiers from `references/tools-reference.md` (e.g. `jira_project_key`, `github_owner`, `github_repo`, `slack_channel`). Rows with unrecognized display names (custom tools, environments) are stored using the row's display name lowercased and underscored as the key.

   `team_profile`:
   ```json
   {
     "members": [
       {
         "name": "Anderson Monroy",
         "role": "tech_lead",
         "hours_per_day": 8,
         "reviewer": true,
         "notes": "",
         "accounts": { "jira": "712020:abc", "github": "andersonm" }
       }
     ],
     "roles": { "tech_lead": 1, "senior_developer": 1 },
     "constraints": "Anderson is part-time Wed–Fri"
   }
   ```

   `roles` includes only keys with count > 0. Unmapped roles count under `"other"`.

3. Display:
   ```
   ✓ governance.md finalized
     Members:     {n}
     Tools:       {list}
     Roles:       {role}: {n}, ...
     Constraints: {summary or "none"}
   ```

4. Execute `{workflow.on_complete}`.
5. Invoke `bmad-help` to surface next-skill suggestions.

The calling skill receives `team_profile` and `project_resources` in-context and continues its own flow.
