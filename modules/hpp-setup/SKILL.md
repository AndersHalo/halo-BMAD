---
name: hpp-setup
description: Install or reconfigure the Halo Product Module — sets up team governance, roadmap builder, and prototype builder with shared project configuration. Use when starting a new project or updating Halo Product Module settings.
---

# Halo Product Module Setup

## Overview

Installs the Halo Product Module (HPP) by collecting project configuration, registering all bundled skills in `_bmad/module-help.csv`, and creating output directories. Run again anytime to reconfigure. Bundles: `team-governance`, `roadmap-build`, `prototype-build`.

## Conventions

- Bare paths resolve from `{skill-root}` (where `customize.toml` lives).
- `{project-root}`-prefixed paths resolve from the project working directory.
- `{workflow.<name>}` resolves to the merged `customize.toml` `[workflow]` table.
- Module identity is defined in `assets/module.yaml`.

## On Activation

1. Resolve customization: `python3 {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --key workflow`. On failure, read `{skill-root}/customize.toml` directly and use defaults.
2. Execute each entry in `{workflow.activation_steps_prepend}` in order.
3. Treat every entry in `{workflow.persistent_facts}` as foundational context.
4. Load `{project-root}/_bmad/core/config.yaml` (and `config.user.yaml` if present); resolve `{user_name}`, `{communication_language}`. Missing → neutral defaults; never block.
5. Read `assets/module.yaml` in full to load module identity and config variable definitions.
6. Detect mode. **Headless** when: no TTY, programmatic caller, `activation_steps_prepend` declares headless, or first message pre-supplies all required inputs. If headless: apply all defaults silently and skip to Run Scripts.

Execute each entry in `{workflow.activation_steps_append}` in order.

Activation is complete. Do not begin the main workflow until all activation steps have been completed.

## Detect Install Mode

Check whether `{project-root}/_bmad/config.yaml` contains an `hpp` section.

- **Fresh install:** no `hpp` section found — display:
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Installing Halo Product Module
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- **Reconfiguration:** `hpp` section exists — display:
  ```
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Reconfiguring Halo Product Module
    (existing settings shown as defaults)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
  Load existing values from `hpp` section as pre-filled defaults for the prompts below.

## Collect Configuration

For each config variable defined in `assets/module.yaml`, present the prompt and collect a value. Show existing values as defaults for reconfiguration.

Present one question at a time:

**governance_dir** — Where should the team governance file be saved?
- Default: `docs/governance`
- Result: `{project-root}/{value}/governance.md`

**roadmap_output_dir** — Where should roadmap files be saved?
- Default: `docs/roadmap`
- Result: `{project-root}/{value}/{product-name}/`

**prototype_output_dir** — Where should prototype files be saved?
- Default: `docs/prototypes`
- Result: `{project-root}/{value}/{prototype-name}/`

After all prompts, display a confirmation summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Configuration summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Governance dir:     {value}
Roadmap output:     {value}
Prototype output:   {value}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Ask:
> Confirm or type a setting name to change it (e.g. `governance_dir`):

Accept freeform changes. Re-display summary after each change. Proceed when confirmed.

## Run Scripts

Run the following scripts. If any script fails, display the error and ask: > Retry, skip, or abort?

**1. Merge config:**
```bash
python3 {skill-root}/scripts/merge-config.py \
  --module hpp \
  --config-path {project-root}/_bmad/config.yaml \
  --user-config-path {project-root}/_bmad/config.user.yaml \
  --values governance_dir="{governance_dir}" roadmap_output_dir="{roadmap_output_dir}" prototype_output_dir="{prototype_output_dir}"
```

**2. Merge help CSV (in parallel with step 1):**
```bash
python3 {skill-root}/scripts/merge-help-csv.py \
  --module hpp \
  --source {skill-root}/assets/module-help.csv \
  --target {project-root}/_bmad/module-help.csv
```

**3. Remove legacy directories (after steps 1 and 2 complete):**
```bash
python3 {skill-root}/scripts/cleanup-legacy.py \
  --module hpp \
  --bmad-dir {project-root}/_bmad \
  --skills-dir {project-root}/.claude/skills
```

**4. Create output directories:**

Create the following directories if they do not exist:
- `{project-root}/{governance_dir}/`
- `{project-root}/{roadmap_output_dir}/`
- `{project-root}/{prototype_output_dir}/`

## Finalize

Display the module greeting from `assets/module.yaml`:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Welcome to the Halo Product Module! Run hpp-setup again anytime to reconfigure.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Display the post-install notes:

```
Next steps:
  1. Configure your team with /team-governance
  2. Generate a roadmap with /roadmap-build
  3. Build a prototype with /prototype-build

Tip: Run team-governance first — roadmap-build uses your team profile for effort estimates.
```

Execute `{workflow.on_complete}`.
Invoke `bmad-help` to surface next-skill suggestions.
