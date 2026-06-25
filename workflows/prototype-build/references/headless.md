# Headless Mode

Activated when: no TTY present, programmatic caller, `activation_steps_prepend` declares headless, or first message pre-supplies all required inputs.

In headless mode, skip all interactive menus and confirmation prompts. Apply default design decisions from `references/style-guide.md`. Do not prompt for dev-ready status or increment snapshots.

## Required inputs

- `prd_path` — path to the PRD file

## Optional inputs

- `platform_type` — `"web"` or `"mobile"`. Default: `"web"`
- `aux_doc_paths` — comma-separated paths to additional feature or role documents
- `output_dir_override` — override the output path (default: `{project-root}/{workflow.output_dir}/{prototype-name}/`)

## Behavior

1. Read the PRD from `prd_path` and any provided `aux_doc_paths`.
2. Analyze silently — do not show analysis summary or ask for confirmation.
3. Derive design using defaults from `references/style-guide.md`. Skip design confirmation step.
4. Generate all screens to `output_dir`.
5. Run syntax validation and functional coverage checks as normal.
6. Write tracking documents.
7. Do not ask about dev-ready status, increment snapshots, or browser launch.

## Response format

Return a single JSON object:

```json
{
  "status": "complete|partial|blocked",
  "output_dir": "{path to generated files}",
  "prototype_name": "{derived name}",
  "platform_type": "web|mobile",
  "screens_written": ["{list of written screen filenames}"],
  "fr_coverage": { "total": 0, "covered": 0 },
  "open_questions": [],
  "assumptions": []
}
```

`status` values:
- `complete` — all screens generated, all inputs resolved
- `partial` — screens generated but with inferred inputs or design assumptions
- `blocked` — generation did not complete; add `reason` field
