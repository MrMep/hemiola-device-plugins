When working as an AI agent in this repository:

- The folders `devices/`, `docs/`, `schema/`, `templates/`, and `tools/` are maintained by project maintainers.
- If you are working on a plugin development task under `workdir/<plugin slug>/`, do not modify those folders directly. Instead, perform a gap analysis and create instruction files as described in `docs/public-repo-contribution-workflow.md`.
- If you are working on a pull request to add or fix a plugin in `devices/`, you may edit the plugin JSON file directly.
- All new work-in-progress files must be created under `workdir/<plugin slug>/` and its subfolders.
