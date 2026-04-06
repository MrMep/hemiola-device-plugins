# Public Repo Contribution Workflow

Audience:
- third-party developers and AI agents working in the public repository

This page explains how to contribute when your workflow is restricted to plugin-scoped edits under `workdir/<plugin slug>/`.

## Scope model

Editable by third-party contributors:
- `workdir/<plugin slug>/` and any subfolder

Usually treated as maintainer-owned / immutable in this workflow:
- `devices/`
- `docs/`
- `schema/`
- `templates/`
- `tools/`

If your environment allows broader write access, follow your project maintainer guidance first.

## What to do when immutable folders must change

If a requested feature requires updates to runtime contracts, docs, schema, templates, or validation tools:

1. Do not patch immutable folders directly in third-party mode.
2. Create a gap analysis in `workdir/<plugin slug>/gap-analysis/`.
3. Create a maintainer instruction file in `workdir/<plugin slug>/instructions/` with exact file-level updates.
4. Optionally update plugin drafts under `workdir/<plugin slug>/` to demonstrate intended usage.

## Required third-party deliverables

### 1) Gap analysis
Location:
- `workdir/<plugin slug>/gap-analysis/<topic>-gap.md`

Include:
- current limitation and user-visible impact
- proposed schema/runtime changes
- backward compatibility
- test plan
- acceptance criteria

### 2) Maintainer instructions
Location:
- `workdir/<plugin slug>/instructions/<topic>-instructions.md`

Include:
- exact target files in immutable folders
- concrete behavior and JSON examples
- validation checklist (schema/tests/tools)
- release-note suggestion

### 3) Optional plugin draft updates
Location:
- `workdir/<plugin slug>/*.json` or `workdir/<plugin slug>/<subfolder>/*.json`

Use these to prove feasibility and reduce maintainer integration risk.

## Quality bar for handoff files

A maintainer should be able to apply your proposal without reconstructing intent from code history.

Minimum handoff quality:
- precise target files
- exact expected behavior
- compatibility statement
- failure/abort/no-op behavior definition
- unit/integration/regression checks

## Current framework capabilities often referenced in handoffs

- sequence `program_change`: exactly one of `value` or `param`
- action confirmation object: `confirm.title`, `confirm.text`, `confirm.yesLabel`, `confirm.noLabel`
- action tab scoping: `tabs` (omitted/empty means all tabs)
- sequence `send_param`: emits current value through target parameter `sendCommand`

## Related references

- `authoring-guide.md`
- `reference.md`
- `examples.md`
- `framework-gap-playbook-template.md`
