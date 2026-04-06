# Contributing to Hemiola Device Plugins

Thanks for your interest in contributing a device plugin!

## How to contribute a new plugin

1. **Fork** this repository and create a feature branch.
2. **Read** [`docs/authoring-guide.md`](docs/authoring-guide.md) for the end-to-end workflow.
3. **Pick a template** from `templates/` that matches your device protocol:
   - `plugin.cc.template.json` — CC-only devices
   - `plugin.sysex.template.json` — bank-based SysEx devices
   - `plugin.template.json` — mixed protocol devices
4. **Create** your plugin as `devices/<slug>.json`.
5. **Validate** against the schema:
   ```bash
   python tools/validate_plugins.py
   ```
6. **Test** against real hardware or Hemiola Plugin Developer Mode.
7. **Open a Pull Request** with a clear description of:
   - the device name and manufacturer
   - how you tested the plugin
   - any known limitations

## Fixing or improving existing plugins

- Open an issue first describing the problem or improvement.
- Reference the specific device slug.
- Include packet captures or test evidence where possible.

## Working with AI

If you are using an AI assistant, follow [`docs/ai-playbook.md`](docs/ai-playbook.md) to generate a disciplined first draft.

## Detailed workflow

See [`docs/public-repo-contribution-workflow.md`](docs/public-repo-contribution-workflow.md) for the full contribution process, including how to handle cases where your plugin needs features not yet in the schema.

## Validation

All plugin JSON files must pass schema validation before merge. The CI pipeline runs this automatically on every PR.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
