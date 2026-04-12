# Plugin Authoring Guide

This guide explains how to design a new Hemiola JSON plugin from scratch.

It is written for human developers, but the structure is deliberate: if an AI agent follows this guide and the companion reference, it should be able to generate a solid first draft given a device MIDI implementation chart and some protocol examples.

## 1. Decide the protocol family first

Every plugin starts by choosing `protocol.type`.

Use `cc` when:

- the device is configured entirely through standard CC messages
- each parameter can be written independently
- the device does not require bulk SysEx read/write state

Use `sysex` when:

- the device exposes one or more bulk SysEx banks
- parameter values are stored at fixed byte offsets inside incoming SysEx frames
- the normal save flow is: read bank, edit bytes, write full bank back

Use `mixed` when:

- some parameters use CC, some NRPN, some SysEx, some Program Change
- the device sends CC feedback instead of bank dumps
- you want explicit per-parameter `sendCommand` control

Rule of thumb:

- if the implementation chart looks like a matrix of CC numbers, start with `cc`
- if the chart shows request/response SysEx frames and memory maps, start with `sysex`
- if the chart mixes multiple message families, use `mixed`

## 2. Gather the source information

Before writing JSON, collect this information in one place.

Required:

- device marketing name
- plugin slug
- trigger strings that appear in the MIDI device name
- MIDI channel behavior
- all writable parameters you want to expose
- logical ranges for those parameters

Strongly recommended:

- raw packet captures from the official editor or the device itself
- examples of connect-time read requests
- examples of successful writes
- patch/program list if the device exposes one
- any checksum rules

If you only have a MIDI implementation chart, extract the following columns into a table:

- parameter name
- message family
- raw address or controller number
- raw range
- default value
- read behavior
- write behavior
- human-friendly label

## 3. Define the top-level metadata

Every plugin begins with:

```json
{
  "slug": "mydevice",
  "name": "My Device",
  "version": "1.0.0",
  "enabled": true,
  "triggers": ["My Device", "MYDEVICE"],
  "requiresLandscape": false,
  ...
}
```

Guidelines:

- `slug` should be stable and filesystem-safe
- `name` is the user-facing display name
- `version` is the plugin document version, not the device firmware version
- `enabled` allows shipping a plugin file without registering it
- `triggers` should include realistic substrings from the actual MIDI port names
- `requiresLandscape` should be `true` only if the UI truly becomes unusable in portrait

## 4. Model the protocol block

### 4.1 `onConnect`

`onConnect` is the list of raw MIDI messages sent when the device connects.

Typical uses:

- request current settings
- request battery state
- request patch list
- enable a live key stream

Example:

```json
"protocol": {
  "type": "sysex",
  "channel": 0,
  "autoWrite": true,
  "onConnect": [
    { "bytes": "F0 47 7F 6D 40 00 00 F7" },
    { "bytes": "F0 47 7F 6D 42 00 00 F7" }
  ],
  "responses": []
}
```

### 4.2 `responses`

Define a `response` whenever the runtime needs to recognize and store an incoming SysEx frame.

Typical reasons:

- a bank contains editable parameter bytes
- a frame carries battery percentage
- a frame contributes entries to a dynamic patch list
- a frame carries live key state
- a frame carries custom fingering slots

Minimal response:

```json
{
  "id": "bank0",
  "match": "F0 47 00 6D 00 00 06"
}
```

The `match` bytes are a header prefix. A frame matches if its leading bytes are identical.

### 4.3 Read/write behavior in `sysex`

Bulk SysEx plugins usually work like this:

1. request one or more banks in `onConnect`
2. incoming frames are stored under `responses[].id`
3. each parameter points into one bank via `source` and `byteIndex`
4. changing a parameter edits the in-memory bank buffer
5. pressing `writeAll` sends the whole bank back

Use `protocol.autoWrite: true` only when the device expects a full bank write after every small change.

### 4.4 `writePrefix`, `writeLength`, `checksumType`

These fields are only needed when the incoming frame is not directly writable as-is.

Use `writePrefix` when:

- the write message is the same bank but with a different header

Use `writeLength` when:

- the response frame is longer than the write frame
- the device expects fixed-size writes

Use `checksumType` when:

- the runtime must rewrite the checksum before sending the bank back

Currently supported response checksum rewrite:

- `robkoo_xor`

## 5. Define parameters

Parameters are the core model. Every UI control eventually maps to one or more `parameters`.

There are three common styles.

### 5.1 Plain CC parameter

```json
{
  "id": "volume",
  "cc": 7,
  "min": 0,
  "max": 127,
  "default": 100
}
```

### 5.2 Bulk SysEx bank parameter

```json
{
  "id": "breathGain",
  "source": "bank0",
  "byteIndex": 7,
  "min": 0,
  "max": 127,
  "default": 64
}
```

### 5.3 Mixed explicit send command

```json
{
  "id": "breathCurve",
  "min": 0,
  "max": 4,
  "default": 2,
  "sendCommand": {
    "type": "sysex",
    "checksum": "ae01",
    "bytes": "F0 41 10 00 00 00 5A 12 00 27 34 13 $V $CS F7",
    "transform": { "inputMin": 0, "inputMax": 4, "outputMin": 1, "outputMax": 5 }
  }
}
```

## 6. Convert raw values into logical values

Use these tools depending on the device encoding:

- `transform` for linear mappings
- `valueOffset` for shifted raw values
- `valueInvert` for reversed scales
- `sendValueMap` and `receiveValueMap` for discrete exceptions

## 7. Choose the right send command type

Supported types:

- `cc`
- `cc14`
- `program_change`
- `nrpn`
- `sysex`
- `multi_sysex`
- `cc_pair`
- `cc_pair_14bit`
- `cc_index_toggle`
- `cc_sequence`

Use the simplest one that exactly matches the protocol.

## 8. Build the UI last

Once the data model works, add `ui`.

Recommended order:

1. tabs
2. sections
3. controls
4. actions
5. optional help

## 9. Start with a minimal working UI

Do not start with a full editor for every parameter.

Prefer this order:

1. one tab
2. one section
3. two or three controls that prove the protocol path works
4. one action only if the device really needs it

Once that works, expand the plugin incrementally.

## 10. Validate in Hemiola Plugin Developer Mode

The host app supports a sandboxed validation flow for plugin authors.

Use it like this:

1. connect the target MIDI device
2. long-press the Config Tool icon in the app bar
3. confirm the Hemiola Plugin Developer Mode dialog
4. select the JSON file to test

Before the plugin is loaded, the host app validates the JSON structure and runtime instantiation. Invalid files are rejected with a warning dialog.

If the file is valid, the plugin is rendered in sandbox mode:

- inbound MIDI still reaches the plugin
- outbound MIDI is intercepted and appended to a queue at the bottom of the screen
- `Send` transmits the entire queued batch
- `Clear` removes the queued messages
- `Exit` leaves sandbox mode

This is intentionally not a sideload path. The plugin is not installed permanently and is not registered for later app launches.

## 11. Final validation checklist

Before proposing a plugin for inclusion, verify all of the following:

- schema validation passes
- the plugin loads in Hemiola Plugin Developer Mode
- invalid values and malformed JSON fail cleanly during testing
- connect-time requests do not spam the device unexpectedly
- outbound messages match packet captures or device documentation
- advanced widgets behave correctly with live device traffic
- the plugin still works after exiting and re-entering sandbox mode

## Public-repo restricted contribution mode

When working as a third-party contributor in environments that restrict edits to `workdir/<plugin slug>/`, use this process:

1. implement plugin drafts and experiments under `workdir/<plugin slug>/`
2. if framework/docs/schema/tooling updates are required, write a gap analysis under `workdir/<plugin slug>/gap-analysis/`
3. create a maintainer instruction file under `workdir/<plugin slug>/instructions/` with exact target-file updates
4. hand off the instruction file for maintainer application in immutable folders

Read `public-repo-contribution-workflow.md` for the complete checklist and handoff quality bar.

If you are using AI to draft a plugin and the device needs behavior not supported by the current framework, follow the framework-gap escalation rule in [AI Playbook](ai-playbook.md) and generate a dedicated gap playbook for the master project instead of inventing unsupported plugin fields. Use [Framework Gap Playbook Template](framework-gap-playbook-template.md) to keep requests consistent.

For a first plugin draft, prefer these controls:

- `knob`
- `slider`
- `dropdown`
- `toggle`
- `tile_picker`
- `cc_select`

Do not start with advanced widgets unless you already understand the incoming live data format.

### Control type best practices

- **Always prefer `tile_picker` over `dropdown`** when the number of options is less than 5. Tile pickers give better at-a-glance visibility and require fewer taps.
- **Always prefer `knob` over `slider`**, unless a slider is explicitly more appropriate (e.g. the parameter conceptually maps to a linear fader or a left-right pan). Knobs are more compact, allow finer control, and fit the instrument-panel aesthetic of the app.
- Use the `color` field to visually group related controls. It is supported on both `knob` and `toggle` types. Give controls in the same functional section a similar hue.
- Consecutive `toggle` controls in the same section are automatically placed on one row, so there is no need to set `inline: true` on them manually.

## 10. Validate the plugin in this order

1. file parses as JSON
2. plugin loads and registers
3. connect-time requests are sent
4. expected responses match
5. parameters update from device state
6. each outbound control sends the expected MIDI
7. `writeAll` or `request` action works end-to-end
8. labels, ranges, and defaults make sense to musicians

## 11. How to go from a MIDI implementation chart to a first draft

For each chart row:

1. classify it as editable parameter, read-only status, action, patch/program, or unsupported
2. group it by transport: CC, NRPN, Program Change, SysEx request, SysEx response, SysEx write
3. infer plugin shape: `cc`, `sysex`, or `mixed`
4. normalize logical ranges and defaults
5. build a small v0 first, not the whole chart at once

## 12. What the MIDI chart usually does not tell you

Expect to discover these experimentally:

- actual device name strings for `triggers`
- packet headers used by official software
- whether checksums are computed over headers, payload, or both
- whether a response frame can be reused as a write frame
- whether writes must be padded or truncated
- bit ordering inside packed live-key bytes
- how program numbers map to human names

## 13. Release checklist

Before publishing a plugin, confirm:

- slug is stable
- `enabled` is correct
- all triggers are realistic
- defaults match the device or a safe neutral state
- outgoing messages are verified on hardware
- help text is musician-facing and accurate
- at least one example packet capture was used to confirm the behavior