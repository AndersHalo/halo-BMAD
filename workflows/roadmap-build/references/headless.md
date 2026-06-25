# Headless Mode

Activated when: no TTY present, programmatic caller, `activation_steps_prepend` declares headless, or first message pre-supplies all required inputs.

In headless mode, skip all interactive menus and confirmation prompts. Use defaults from `customize.toml` for any unspecified optional inputs.

## Required inputs

- `prd_path` — path to the PRD file

## Optional inputs

- `format_selection` — `1` (Now/Next/Later), `2` (Theme-Based), `3` (Goal-Oriented), `4` (Gantt), `5` (All four). Default: `5`
- `feature_file_paths` — comma-separated paths to feature spec files
- `architecture_path` — path to architecture document
- `sprint_file_path` — path to Jira CSV or markdown task board
- `gantt_start` — Gantt chart start date (ISO 8601). Default: today

## Behavior

1. Read the PRD from `prd_path`. Derive `product_name` from the PRD title.
2. Read any provided optional documents.
3. Analyze documents and estimate all initiatives using solo-developer baseline (or governance_path if available).
4. Generate all requested formats to `{workflow.output_dir}/{product_name}/`.
5. Do not ask for markdown export — skip it in headless mode.
6. Do not prompt for versioning — write to v1 or increment silently.

## Response format

Return a single JSON object:

```json
{
  "status": "complete|partial|blocked",
  "output_dir": "{path to generated files}",
  "product_name": "{derived name}",
  "files_written": ["{list of written files}"],
  "roadmap_version": 1,
  "any_sprint_coverage": false,
  "open_questions": [],
  "assumptions": []
}
```

`status` values:
- `complete` — all files generated, all inputs resolved
- `partial` — files generated but with inferred inputs or open questions
- `blocked` — generation did not complete; add `reason` field
