# Headless Mode

Activated when: no TTY present, programmatic caller, `activation_steps_prepend` declares headless, or first message pre-supplies all required inputs.

In headless mode, skip all interactive menus and confirmation prompts. Use `{workflow.default_hours_per_day}` and role defaults from `references/team-roles-reference.md` for any unspecified member fields.

## Required inputs

- `tools` — list of platform tool slugs to configure (e.g. `["jira", "github"]`)
- `members` — list of member objects: `{ name, role, hours?, reviewer?, accounts? }`

## Optional inputs

- `constraints` — free-text scheduling or availability notes

## Behavior

1. Configure project resources from `tools` input using field defaults where values are not provided.
2. Register all members from `members` input. Apply role defaults from `references/team-roles-reference.md`.
3. Write `{project-root}/{workflow.governance_dir}/governance.md` directly — no interactive review step.
4. Do not prompt for confirmation at any step.

## Response format

Return a single JSON object:

```json
{
  "status": "complete|partial|blocked",
  "governance_path": "{project-root}/{governance_dir}/governance.md",
  "members_written": 0,
  "tools_configured": [],
  "open_questions": [],
  "assumptions": []
}
```

`status` values:
- `complete` — governance.md written, all inputs resolved
- `partial` — governance.md written but with inferred values or open questions
- `blocked` — governance.md not written; add `reason` field
