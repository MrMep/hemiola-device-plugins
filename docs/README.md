# Plugin Documentation

This documentation is split by purpose.

## Read in this order

1. `authoring-guide.md`
   End-to-end workflow for turning a device into a Hemiola plugin.

2. `public-repo-contribution-workflow.md`
   Workflow and handoff rules for third-party contributors working in restricted public-repo mode.

3. `reference.md`
   Complete JSON schema reference, field semantics, supported command types, UI controls, and runtime behaviors.

4. `examples.md`
   Minimal and advanced examples you can copy, trim, and adapt.

5. `ai-playbook.md`
   How to generate a first plugin draft from a MIDI implementation chart using AI, including a high-signal prompt template.

6. `faq.md`
   Common pitfalls, edge cases, and debugging answers.

7. `../schema/hemiola-plugin.schema.json`
   Machine-readable schema for validation, autocomplete, and AI output constraints.

## Templates

- `../templates/plugin.cc.template.json`: for CC-only devices
- `../templates/plugin.sysex.template.json`: for bank-based SysEx devices
- `../templates/plugin.template.json`: for generic mixed-protocol devices

## What a plugin can do

A Hemiola plugin can:

- identify a device by name or trigger strings
- request device state on connect
- read incoming SysEx and CC feedback
- send CC, NRPN, Program Change, SysEx, and command sequences
- render a full Flutter-native configuration UI from JSON
- expose built-in presets and help pages
- support device-specific advanced widgets such as pressed-key displays and custom fingering editors

## What you typically need from the device

Best case:

- MIDI implementation chart
- SysEx read/write specification
- one or more real packet captures from the device
- list of program names or patch names
- mapping of any bit-packed status bytes

Minimum viable input for AI-assisted generation:

- MIDI implementation chart
- at least one example of any non-trivial SysEx packet family
- a short note describing whether the device is CC-only, bulk-SysEx, or mixed

## Important limits

The MIDI implementation chart alone is often enough for a first plugin draft, but not always enough for a production-ready plugin.

You usually need extra empirical information when the device has:

- proprietary checksums
- bank dumps with undocumented byte offsets
- dynamic patch names
- key-state bitfields
- custom fingering memories
- special write prefixes or write lengths

The right workflow is therefore:

1. generate a draft from the chart
2. validate it against real traffic
3. refine undocumented behaviors with packet captures

## Host app sandbox testing

For hands-on validation in the host app, use Hemiola Plugin Developer Mode.

That flow lets you load a JSON file temporarily from the Config Tool via long-press, validates it before load, and renders it in a sandbox where outbound MIDI is queued instead of being sent automatically.

Read `authoring-guide.md` for the full sandbox workflow.