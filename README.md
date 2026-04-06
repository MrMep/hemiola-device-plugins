# Hemiola Device Plugins

Hemiola device plugins are JSON documents that describe how a MIDI device is detected, how it exchanges data, and how its configuration UI is rendered inside [Hemiola](https://hemiola.app).

This repository is the public home of those plugins, their documentation, and the supporting tooling around them.

## Why this exists

The goal is to make new device support practical without editing app code every time.

The JSON runtime already supports:

- plain CC-based devices
- bulk SysEx devices
- mixed CC, NRPN, SysEx, and Program Change devices
- dynamic patch lists
- per-parameter transforms and value maps
- embedded help sections
- preset-like UI controls
- live pressed-key visualizations
- advanced custom fingering managers for supported device families

That means many devices can be integrated declaratively.

## Repository layout

- `devices/`: publishable plugin JSON files
- `docs/`: authoring, reference, examples, AI workflow, FAQ
- `schema/`: machine-readable JSON schema for validation and editor integration
- `templates/`: valid starting points for new plugins
	- `plugin.template.json`: generic mixed-protocol starter
	- `plugin.cc.template.json`: CC-only starter
	- `plugin.sysex.template.json`: bank-based SysEx starter
- `tools/validate_plugins.py`: validates plugin JSON against the schema
- `dist/`: generated output, not versioned

## Quick start

If you want to add support for a new device:

1. Read `docs/authoring-guide.md`
2. Keep `docs/reference.md` open while authoring
3. Start from `docs/examples.md`, not from a blank file
4. If using AI, follow `docs/ai-playbook.md`
5. Validate the plugin against `schema/hemiola-plugin.schema.json`
6. Test against real hardware, packet captures, or Hemiola Plugin Developer Mode

Fastest starting point:

1. choose the closest template:
	- `templates/plugin.cc.template.json`
	- `templates/plugin.sysex.template.json`
	- `templates/plugin.template.json` for generic mixed cases
2. rename it to `devices/<slug>.json`
3. edit protocol, parameters, and UI
4. run `python tools/validate_plugins.py`

## Documentation map

- `docs/README.md`: documentation index
- `docs/authoring-guide.md`: end-to-end plugin workflow
- `docs/reference.md`: full JSON field reference and runtime semantics
- `docs/examples.md`: copyable minimal and advanced examples
- `docs/ai-playbook.md`: how to generate a first plugin draft from a MIDI implementation chart
- `docs/faq.md`: common pitfalls and answers

## JSON schema

This repository includes a machine-readable schema:

- `schema/hemiola-plugin.schema.json`

Use it for:

- catching field typos early
- validating plugin structure automatically
- improving editor autocomplete and inline diagnostics
- constraining AI-generated drafts to the runtime model

Local validation command:

```bash
python tools/validate_plugins.py
```

If `jsonschema` is not installed locally:

```bash
python -m pip install jsonschema
```

The schema covers:

- top-level plugin metadata
- protocol, onConnect messages, and responses
- parameters and send commands
- presets
- UI tabs, sections, controls, and actions
- keyboard definitions
- embedded help sections

### Editor integration

To enable autocomplete and inline validation in VS Code, add this to your workspace or user `settings.json`:

```json
{
  "json.schemas": [
    {
      "fileMatch": ["/devices/*.json", "/templates/*.json"],
      "url": "./schema/hemiola-plugin.schema.json"
    }
  ]
}
```

## Plugin anatomy

At a high level, a plugin looks like this:

```json
{
	"slug": "mydevice",
	"name": "My Device",
	"triggers": ["My Device"],
	"protocol": { ... },
	"parameters": [ ... ],
	"ui": { ... }
}
```

The design flow is usually:

1. classify the device as `cc`, `sysex`, or `mixed`
2. model parameters and message mappings
3. add the UI layer
4. validate and test against the real device

## AI-assisted plugin generation

This repo is intentionally documented so that a human can create a plugin by hand and an AI can create a disciplined first draft from a MIDI implementation chart.

The intended AI workflow is:

1. feed the MIDI implementation chart and any raw packets to the AI
2. force the AI to classify the protocol family first
3. generate a small first plugin draft
4. validate it against the JSON schema
5. refine against real device traffic

Important constraint:

The MIDI implementation chart alone is often enough for a first draft, but often not enough for a production-ready plugin when the device has proprietary SysEx details, custom checksums, bitfields, or memory editors.

## Developer Mode

Hemiola includes a Plugin Developer Mode for validating plugins against real hardware without permanently installing them.

Developer Mode flow:

1. open Hemiola and connect the target MIDI device
2. long-press the Config Tool icon
3. confirm the developer-mode warning
4. choose a plugin JSON file to validate
5. if the file is valid, Hemiola renders it in sandbox mode for the current device

Sandbox behavior:

- incoming MIDI from the device still reaches the plugin
- outbound MIDI generated by the plugin is captured into a queue instead of being sent immediately
- the queue is visible at the bottom of the screen and can be edited manually
- `Send` flushes the queued messages to the device
- `Clear` empties the queue
- `Exit` closes sandbox mode and restores normal Config Tool behavior
- invalid JSON files are rejected before load with a warning dialog

This workflow is for validation only. It does not register, install, or persist the plugin.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit a new plugin or improve an existing one.

## Intended audience

This repository is for:

- developers adding support for new MIDI devices
- maintainers reviewing plugin quality and correctness
- AI-assisted workflows that need a precise target format

The docs are written for humans first, but they are also explicit enough to support constrained AI generation.

## License

This project is licensed under the [MIT License](LICENSE).