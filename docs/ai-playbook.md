# AI Playbook

This document explains how to generate a new Hemiola plugin with AI from a MIDI implementation chart.

The goal is a disciplined first draft that is easy for a human to validate and finish.

## 1. What the AI should receive

Best input package:

- MIDI implementation chart
- any SysEx specification pages
- one or more example request/response packets
- device name as it appears in MIDI ports
- any known checksum notes
- any known program list or patch names

Minimum acceptable input package:

- MIDI implementation chart
- short note saying whether the device is CC-only, SysEx bank-based, or mixed

## 2. What the AI should produce

Ask the AI to return:

1. protocol classification
2. assumptions and unknowns
3. plugin JSON draft
4. short validation checklist
5. list of fields that still need packet captures or hardware confirmation

If the AI cannot infer some fields reliably, it should leave them out rather than invent them.

## 3. What the AI can infer reliably

Usually inferable from the chart alone:

- whether the plugin should be `cc`, `sysex`, or `mixed`
- parameter ids and labels
- raw ranges and defaults
- CC numbers
- NRPN address pairs
- Program Change usage
- obvious transforms between UI ranges and MIDI ranges

## 4. What the AI cannot infer reliably from the chart alone

Usually not inferable without packet captures or experimentation:

- `triggers`
- `match` headers for actual device frames if the chart is vague
- `writePrefix`
- `writeLength`
- exact checksum coverage rules
- `bitOrder` for live key streams
- slot layouts for custom fingering editors
- whether official software uses one bank or many banks
- hidden write-only or read-only bytes surrounding editable values

## 5. Prompt template

Use this template as the starting point.

```text
You are generating a Hemiola JSON device plugin.

Target runtime constraints:
- Top-level fields: slug, name, version, enabled, triggers, requiresLandscape, protocol, parameters, presets, ui, help.
- protocol.type must be one of: cc, sysex, mixed.
- Parameters may use legacy cc fields, bulk SysEx source+byteIndex fields, or explicit sendCommand.
- Supported sendCommand types: cc, nrpn, sysex, multi_sysex, program_change, cc_pair, cc_sequence.
- Supported UI controls: slider, dropdown, toggle, knob, tile_picker, preset_picker, cc_select, pressed_keys, custom_fingering_manager.
- If information is missing, do not invent advanced behaviors. Omit them and list them as open questions.

Your task:
1. Read the MIDI implementation chart below.
2. Decide whether the plugin should be cc, sysex, or mixed.
3. Extract the parameters that are worth exposing in a first public plugin.
4. Produce a valid plugin JSON draft.
5. After the JSON, provide:
   - assumptions
   - unresolved items
   - hardware validation checklist

Design rules:
- Prefer a small correct plugin over a large speculative one.
- Use descriptive parameter ids.
- Use logical user-facing ranges when possible.
- Use transforms, offsets, or value maps only when justified by the chart.
- Only use pressed_keys or custom_fingering_manager if the input explicitly documents those formats.
- If the chart only documents CC/NRPN/program change, do not fabricate SysEx support.

Input material:
[PASTE MIDI IMPLEMENTATION CHART HERE]

Additional notes:
[PASTE ANY RAW PACKETS OR HUMAN NOTES HERE]
```

## 6. AI validation rubric

A human reviewer should reject the AI draft if it does any of the following:

- invents undocumented SysEx headers
- invents checksums without stating uncertainty
- uses advanced controls without incoming data format evidence
- exposes dozens of undocumented bytes as user controls
- uses vague parameter ids such as `param1`, `value2`, `unknown3` for real known fields

## 7. Recommended AI workflow in practice

Phase 1:

- feed only the chart
- ask for a small initial plugin draft

Phase 2:

- add real packet captures
- ask the AI to reconcile the draft with observed traffic

Phase 3:

- ask for final cleanup of labels, tabs, presets, and help text

## 8. Human handoff checklist after AI generation

Once the AI produces a draft, a human should verify:

1. JSON parses
2. protocol family is correct
3. all ranges are sensible
4. all labels are user-facing
5. all CC/NRPN numbers match the chart
6. all SysEx templates match real packets
7. all uncertainties are tracked before release

## 9. Framework gap escalation rule

If the requested plugin requires behavior that the current plugin framework does not support, the AI must not invent unsupported JSON fields or runtime semantics.

Instead, the AI must produce a separate and explicit "framework gap" playbook that can be fed into the master project.

Use this ready-to-copy template:

- [Framework Gap Playbook Template](framework-gap-playbook-template.md)

That gap playbook should include at least:

1. missing capability description
2. why existing schema/runtime cannot express it
3. minimal proposed schema and runtime changes
4. backward-compatibility notes
5. validation and test checklist for the framework update

Until that framework gap is implemented in the master project, the plugin draft should stay within currently supported features and clearly list the blocked parts.